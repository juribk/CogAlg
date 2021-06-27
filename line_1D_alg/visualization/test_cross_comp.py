'''
For a deeper understanding of CogAlg, I have created a couple of simple functions that visualize cross_comp (image).
The purpose of these functions is to display CP patterns.
The result looks similar at first glance to 4_m.jpg from draw_line_patterns.py, but it is not.
I think it will be useful for checking the result of cross_comp (image)

In the picture: white - Patterns CP, green - sub Patterns CP, blue - sub-sub Patterns CP
'''

import sys
from os.path import dirname, join, abspath
import argparse
from time import time
from utils import *
from line_patterns import cross_comp

sys.path.insert(0, abspath(join(dirname("CogAlg"), '..')))

'''
Adding sub levels 
'''
def Draw_Sub_Layers_CP(img_out, cp, x, y, bright_0):
    if cp.sub_layers: # not empty sub layers
        for sub_pos, sub_list in enumerate(cp.sub_layers[0]):
            Ls, fdP, fid, rdn, rng, sub_cp_list = sub_list
            x_sub = x - 1
            for sub_cp in reversed(sub_cp_list):
                x_sub -= sub_cp.L
                img_out[y, x_sub - 1, 1] = 255
                img_out[y, x_sub - 1, 2] = bright_0
                Draw_Sub_Layers_CP(img_out, sub_cp, x_sub, y, bright_0 + 128 if bright_0 + 128 < 255 else 255)
''' 
Visualization of the cross_comp(image) function
'''
def Draw_Patterns_CP(image, path, frame_of_patterns_):
    img_out = np.zeros_like(image)
    for y, line in enumerate(frame_of_patterns_): # loop each y line
        x = 0
        x_old = 0
        for cp_pos, cp in enumerate(line): # loop each pattern
            x += cp.L
            img_out[y, x - 1] = 255
            Draw_Sub_Layers_CP(img_out, cp, x, y, 0)
            x_old = x;

    cv2.imshow('test', img_out)
    cv2.imwrite(path + 'Patterns_CP.jpg', img_out)

if __name__ == "__main__":
    # Parse argument (image)
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-i', '--image',
                                 help='path to image file',
                                 default='.//raccoon.jpg')
    arguments = vars(argument_parser.parse_args())
    # Read image
    image_c = cv2.imread(arguments['image'], cv2.IMREAD_COLOR)  # load pix-mapped image
    image = cv2.cvtColor(image_c, cv2.COLOR_BGR2GRAY)
    assert image is not None, "No image in the path"
    image = image.astype(int)

    start_time = time()
    # Main
    frame_of_patterns_ = cross_comp(image)  # returns Pm__

    # Visualization of the frame_of_patterns_
    Draw_Patterns_CP(image_c, './/images/line_patterns/', frame_of_patterns_)

    end_time = time() - start_time
    print(end_time)
