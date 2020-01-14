import cv2
import argparse
from time import time
from collections import deque

# pattern filters or hyper-parameters: eventually from higher-level feedback, initialized here as constants:

ave = 10   # |difference| between pixels that coincides with average value of mP - redundancy to overlapping dPs
ave_m = 5   # for m defined as min, same?
ave_M = 127  # min M for initial incremental-range comparison(t_), higher cost than der_comp?
ave_D = 63   # min |D| for initial incremental-derivation comparison(d_)
ave_L = 4    # min L for sub_cluster(d)
ave_nP = 5   # average number of sub_Ps in P, to estimate intra-costs?
ave_rdn_inc = 1 + 1 / ave_nP  # 1.2
ini_y = 500
# min_rng = 1  # >1 if fuzzy pixel comparison range, for sensor-specific noise only

''' 
  line_patterns is a principal version of 1st-level 1D algorithm, contains operations: 

- Cross-compare consecutive pixels within each row of image, forming dert_ queue of derts: tuples of derivatives per pixel. 
  dert_ is then segmented by match deviation into patterns Ps: contiguous sequences of pixels that form same-sign m: +P or -P. 
  Initial match is inverse deviation of variation: m = ave_|d| - |d|, not min: brightness doesn't correlate with predictive value.

- Positive Ps: spans of pixels forming positive match, are evaluated for cross-comp of dert input param over incremented range 
  (positive match means that pixels have high predictive value, thus likely to match more distant pixels).
- Median Ps: |d| is too weak for immediate comp_d, but d sign (direction) may persist, and d sign match is partial d match.
  Then dert_ is segmented by same d sign, accumulating segment sD to evaluate der_comp within a segment.  
- Negative Ps: high-variation spans, are evaluated for cross-comp of difference, which forms higher derivatives.
  (d match = min: rng+ comp value: predictive value of difference is proportional to its magnitude, although inversely so)
  
  Both extended cross-comp forks are recursive: resulting sub-patterns are evaluated for deeper cross-comp, same as top patterns.
  The signs for these forks may be defined independently, for overlaps or gaps in spectrum, but then rdn is far more complex. 

  Initial bi-lateral cross-comp here is 1D slice of 2D 3x3 kernel, while uni-lateral d is equivalent to 2x2 kernel.
  Odd kernels preserve resolution of pixels, while 2x2 kernels preserve resolution of derivatives, in resulting derts.
  The former should be used in comp_rng and the latter in comp_d, which may alternate with intra_comp.
  
  postfix '_' denotes array name, vs. same-name elements
  prefix '_' denotes prior of two same-name variables
  prefix 'f' denotes binary flag
  '''

def cross_comp(frame_of_pixels_):  # converts frame_of_pixels to frame_of_patterns, each pattern maybe nested

    Y, X = image.shape  # Y: frame height, X: frame width
    frame_of_patterns_ = []
    for y in range(ini_y + 1, Y):
        # initialization per row:
        pixel_ = frame_of_pixels_[y, :]  # y is index of new line pixel_
        P_ = []  # row of patterns
        __p, _p = pixel_[0:2]  # each prefix '_' denotes prior
        _d = _p - __p  # initial comp, no /2: effectively *2 for back-projection
        _m = ave - abs(_d)
        if _m > 0:
            if _m > ave_m: sign = 0  # low variation
            else: sign = 1  # medium variation
        else: sign = 2  # high variation
        # initialize P with dert_[0]:
        P = sign, __p, _d, _m, [(__p, _d, _m, None)], []  # sign, I, D, M, dert_, sub_

        for p in pixel_[2:]:  # pixel p is compared to prior pixel _p in a row
            d = p - _p
            m = ave - abs(d)  # initial match is inverse deviation of |difference|
            bi_d = (d + _d) / 2  # normalized bilateral difference
            bi_m = (m + _m) / 2  # normalized bilateral match
            dert = _p, bi_d, bi_m, _d
            # accumulate or terminate mP: span of pixels forming same-sign m:
            P, P_ = form_P(P, P_, dert)
            _p, _d, _m = p, d, m  # uni_d is not used in comp
        # terminate last P in row:
        dert = _p, _d, _m, _d  # no / 2: last d and m are forward-projected to bilateral values
        P, P_ = form_P(P, P_, dert)
        P_ += [P]
        # evaluate sub-recursion per P:
        P_ = intra_P(P_, fid=False, rdn=1, rng=1, sD=0)  # recursive
        frame_of_patterns_ += [P_]  # line of patterns is added to frame of patterns

    return frame_of_patterns_  # frame of patterns will be output to level 2

''' Recursion extends pattern structure to 1d hierarchy and then 2d hierarchy, to be adjusted by macro-feedback:
    P_:
    fid,   # flag: input is derived: magnitude correlates with predictive value: m = min-ave, else m = ave-|d|
    rdn,   # redundancy to higher layers, possibly lateral overlap of rng+, seg_d, der+, rdn += 1 * typ coef?
    rng,   # comp range, + frng | fder?  
    P:
    sign,  # ternary: 0 -> rng+, 1 -> segment_d, 2 -> der+ 
    Dert = I, D, M,  # L = len(dert_) * rng
    dert_, # input for sub_segment or extend_comp
           # conditional 1d array of next layer:
    sub_,  # seg_P_ from sub_segment or sub_P_ from extend_comp
           # conditional 2d array of deeper layers, each layer maps to higher layer for feedback:
    layer_,  # each layer has Dert and array of seg_|sub_s, each with crit and fid, nested to different depth
             # for layer-parallel access and comp, similar to frequency domain representation
    root_P   # reference for layer-sequential feedback 

    orders of composition: 1st: dert_, 2nd: seg_|sub_(derts), 3rd: P layer_(sub_P_(derts))? 
    line-wide layer-sequential recursion and feedback, for clarity and slice-mapped SIMD processing? 
'''

def form_P(P, P_, dert):  # initialization, accumulation, termination, recursion

    _sign, I, D, M, dert_, sub_ = P  # each sub in sub_ is nested to depth = sub_[n]
    p, d, m, uni_d = dert
    if m > 0:
        if m > ave_m: sign = 0  # low variation: eval comp rng+ per P, ternary sign
        else: sign = 1  # medium variation: segment P.dert_ by d sign
    else: sign = 2  # high variation: eval comp der+ per P

    if sign != _sign:  # sign change: terminate P
        P_.append(P)
        I, D, M, dert_ = 0, 0, 0, []  # reset accumulated params
    # accumulate params with bilateral values:
    I += p; D += d; M += m
    dert_ += [(p, d, m, uni_d)]  # uni_d for der_comp and segment
    P = sign, I, D, M, dert_, sub_  # sub_, layer_ accumulated in intra_P

    return P, P_


def intra_P(P_, fid, rdn, rng, sD):  # evaluate for sub-recursion in line P_, filling its sub_P_ with the results

    for sign, I, D, M, dert_, sub_ in P_:  # sub_ is a list of lower pattern layers, nested to depth = sub_[n]

        if sign == 0:  # low-variation P, rdn+1.2: 1 + (1 / ave_nP): rdn to higher derts + ave rdn to higher sub_
            if M > ave_M * rdn and len(dert_) > 4:  # rng+ eval vs. fixed cost = ave_M
                ssub_ = rng_comp(dert_, fid)  # comp rng = 1, 2, 4, kernel = rng * 2 + 1: 3, 5, 9
                rdn += 1 / len(ssub_) - 0.2   # adjust distributed rdn, estimated in intra_P
                sub_ += [ 0, fid, rdn, rng*2, ssub_ ]  # 1st layer
                sub_ += [ intra_P(ssub_, fid, rdn+1.2, rng, 0) ]  # recursion eval and deeper layers feedback

        elif sign == 1 and not sD:  # mid-variation P:
            if len(dert_) > ave_L * rdn:  # low |M|, filter by L only
                ssub_, sD = segment(dert_)  # segment dert_ by ds: sign match covers variable cost?
                rdn += 1 / len(ssub_) - 0.2
                sub_ += [ 1, True, rdn, rng, ssub_]  # 1: ternary fork sign, may differ from P sign
                sub_ += [ intra_P(ssub_, True, rdn+1.2, rng, sD) ]  # will trigger fork 2:

        elif sign == 2 or sD:  # high-variation P or any seg_P:
            if sD: vD = sD  # called after segment(), or filter by L: n of ms?
            else:  vD = -M
            if (vD > ave_D * rdn) and len(dert_) > 4:  # der+ eval, full-P der_comp obviates seg_dP_
                ssub_ = der_comp(dert_)  # cross-comp uni_ds in dert[3]
                rdn += 1 / len(ssub_) - 0.2
                sub_ += [ 2, True, rdn, rng, ssub_]
                sub_ += [ intra_P(ssub_, True, rdn+1.2, rng, 0) ]  # deeper layers feedback

        # each: else merge non-selected sub_Ps within P, if in max recursion depth? Eval per P_: same op, !layer
    return P_  # add return of Dert and hypers, same in sub_[0]? [] fill if min_nP: L, LL?


def segment(dert_):  # P segmentation by same d sign: initialization, accumulation, termination

    sub_ = []  # replaces P.sub_
    sub_D = 1  # bias to trigger 3rd fork in next intra_P
    _p, _d, _m, _uni_d = dert_[1]  # skip dert_[0]: no uni_d; prefix '_' denotes prior
    _sign = _uni_d > 0
    I =_p; D =_d; M =_m; seg_dert_= [(_p, _d, _m, _uni_d)]  # initialize seg_P, same as P

    for p, d, m, uni_d in dert_[2:]:
        sign = uni_d > 0
        if _sign != sign:
            sub_D += abs(D)
            sub_.append((_sign, I, D, M, seg_dert_, []))  # terminate seg_P, same as P
            I, D, M, dert_, = 0, 0, 0, []  # reset accumulated seg_P params
        _sign = sign
        I += p; D += d; M += m  # accumulate seg_P params, or D += uni_d?
        dert_.append((p, d, m, uni_d))
    sub_D += abs(D)
    sub_.append((_sign, I, D, M, seg_dert_, []))  # pack last segment, nothing to accumulate

    return sub_, sub_D  # replace P.sub_


def rng_comp(dert_, fid):  # sparse comp, 1 pruned dert / 1 extended dert to maintain 2x overlap

    sub_P_ = []  # replaces P.sub_; prefix '_' denotes the prior of same-name variables, initialization:
    (__i, __short_bi_d, __short_bi_m, _), _, (_i, _short_bi_d, _short_bi_m, _) = dert_[0:3]
    _d = _i - __i  # initial comp: no /2: effectively *2 for back-projection
    if fid: _m = min(__i, _i) - ave_m + __short_bi_m
    else:   _m = ave - abs(_d) + __short_bi_m
    if _m > 0:
        if _m > ave_m: sign = 0  # low variation
        else: sign = 1  # medium variation
    else: sign = 2  # high variation
    # initialize P with dert_[0]:
    sub_P = sign, __i, _d, _m, [(__i, _d, _m, None)], []  # sign, I, D, M, dert_, sub_

    for n in range(4, len(dert_), 2):  # backward comp, skip 1 dert to maintain overlap rate, that defines ave
        i, short_bi_d, short_bi_m = dert_[n][:3]  # shorter-rng dert
        d = i - _i
        if fid:  # match = min: magnitude of derived vars correlates with stability
            m = min(i, _i) - ave_m + _short_bi_m   # m accum / i number of comps
        else:  # inverse match: intensity doesn't correlate with stability
            m = ave - abs(d) + _short_bi_m
        d += _short_bi_d  # _d and _m combine bi_d | bi_m at rng-1, not normalized for span?
        bi_d = (_d + d) / 2  # bilateral difference, accum in rng
        bi_m = (_m + m) / 2  # bilateral match, accum in rng
        dert = _i, bi_d, bi_m, _d
        _i, _d, _m, _short_bi_d, _short_bi_m = i, d, m, short_bi_d, short_bi_d
        # P accumulation or termination:
        sub_P, sub_P_ = form_P(sub_P, sub_P_, dert)

    # terminate last sub_P in dert_:
    dert = _i, _d, _m, _d  # no / 2: forward-project unilateral to bilateral d and m values
    sub_P, sub_P_ = form_P(sub_P, sub_P_, dert)
    sub_P_ += [sub_P]
    return sub_P_  # replaces P.sub_


def der_comp(dert_):  # comp of consecutive uni_ds in dert_, dd and md may match across d sign

    sub_P_ = []  # return to replace P.sub_, initialization:
    (_, _, _, __i), (_, _, _, _i) = dert_[1:3]  # each prefix '_' denotes prior
    _d = _i - __i  # initial comp
    _m = min(__i, _i) - ave_m
    if _m > 0:
        if _m > ave_m: sign = 0
        else: sign = 1
    else: sign = 2
    # initialize P with dert_[1]:
    sub_P = sign, __i, _d, _m, [(__i, _d, _m, None)], []  # sign, I, D, M, dert_, sub_

    for dert in dert_[3:]:
        i = dert[3]  # unilateral d
        d = i - _i   # d is dd
        m = min(i, _i) - ave_m  # md = min: magnitude of derived vars corresponds to predictive value
        bi_d = (_d + d) / 2  # bilateral d-difference per _i
        bi_m = (_m + m) / 2  # bilateral d-match per _i
        dert = _i, bi_d, bi_m, _d
        _i, _d, _m = i, d, m
        # P accumulation or termination:
        sub_P, sub_P_ = form_P(sub_P, sub_P_, dert)
    # terminate last sub_P in dert_:
    dert = _i, _d, _m, _d  # no / 2: forward-project unilateral to bilateral d and m values
    sub_P, sub_P_ = form_P(sub_P, sub_P_, dert)
    sub_P_ += [sub_P]
    return sub_P_  # replaces P.sub_


if __name__ == "__main__":
    # Parse argument (image)
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-i', '--image',
                                 help='path to image file',
                                 default='.//raccoon.jpg')
    arguments = vars(argument_parser.parse_args())
    # Read image
    image = cv2.imread(arguments['image'], 0).astype(int)  # load pix-mapped image
    assert image is not None, "Couldn't find image in the path!"
    image = image.astype(int)
    # same image loaded online, without cv2:
    # from scipy import misc
    # image = misc.face(gray=True).astype(int)

    start_time = time()
    # Main
    frame_of_patterns_ = cross_comp(image)
    end_time = time() - start_time
    print(end_time)

'''
2nd level cross-compares resulting patterns Ps (s, L, I, D, M, r, nested e_) and evaluates them for deeper cross-comparison. 
Depth of cross-comparison (discontinuous if generic) is increased in lower-recursion e_, then between same-recursion e_s:

comp (s)?  # same-sign only
    comp (L, I, D, M)?  # in parallel or L first, equal-weight or I is redundant?  
        comp (r)?  # same-recursion (derivation) order e_
            cross_comp (e_)
            
Then extend this 2nd level alg to a recursive meta-level algorithm

match=min: local vs. global
'''
