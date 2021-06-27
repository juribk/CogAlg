"""
"""

import sys
import numpy as np
import datetime
import plotly.graph_objects as go
import cv2

from line_patterns import cross_comp

class Visi_Line(object):
    """
    """

    def __init__(self, image = None, frame_patterns = None, pos_line = 0):
        # private
        self._fig = go.Figure()
        self._image = image
        self._frame_patterns = frame_patterns
        self._pos_line = pos_line
        self.__visi__()

    def __norm__(self, data):
        window_min = np.nanmin(data)
        window_max = np.nanmax(data)
        data_norm = np.subtract(data, window_min)
        div = (window_max - window_min) / 255
        data_norm = np.divide(data_norm, div)
        return np.rint(data_norm)


    def __visi__(self):
        """ Let's display the data """
        params_name = ['Image',
                       'dert.p',
                       'dert.d',
                       'dert.m',
                       'P.sign',
                       'P.L',
                       'P.I',
                       'P.D',
                       'P.M',
                       ]
        params_name.reverse()
        params_count = len(params_name)

        x_data = np.arange(len(self._image[self._pos_line]))

        z_data_text = np.full((len(params_name), len(self._image[self._pos_line])), np.NAN)
        z_data_text[params_name.index('Image')] = self._image[self._pos_line + 1] # The first line is the line of the picture

        x_pos = 0
        for pattern in self._frame_patterns[self._pos_line]: # loop each pattern
            # Добавим данные dert
            for x, dert in enumerate(pattern.dert_):
                z_data_text[params_name.index('dert.p'), x_pos + x] = dert.p
                z_data_text[params_name.index('dert.d'), x_pos + x] = dert.d
                z_data_text[params_name.index('dert.m'), x_pos + x] = dert.m

            x_pos += pattern.L
            z_data_text[params_name.index('P.sign'), x_pos - 1] = pattern.sign
            z_data_text[params_name.index('P.L'), x_pos - 1] = pattern.L
            z_data_text[params_name.index('P.I'), x_pos - 1] = pattern.I
            z_data_text[params_name.index('P.D'), x_pos - 1] = pattern.D
            z_data_text[params_name.index('P.M'), x_pos - 1] = pattern.M

        z_data = np.full((len(params_name), len(self._image[self._pos_line])), np.NAN)
        z_data[params_name.index('Image')] = z_data_text[params_name.index('Image')]
        z_data[params_name.index('dert.p')] = self.__norm__(z_data_text[params_name.index('dert.p')])
        z_data[params_name.index('dert.d')] = self.__norm__(z_data_text[params_name.index('dert.d')])
        z_data[params_name.index('dert.m')] = self.__norm__(z_data_text[params_name.index('dert.m')])
        z_data[params_name.index('P.sign')] = self.__norm__(z_data_text[params_name.index('P.sign')])
        z_data[params_name.index('P.L')] = self.__norm__(z_data_text[params_name.index('P.L')])
        z_data[params_name.index('P.I')] = self.__norm__(z_data_text[params_name.index('P.I')])
        z_data[params_name.index('P.D')] = self.__norm__(z_data_text[params_name.index('P.D')])
        z_data[params_name.index('P.M')] = self.__norm__(z_data_text[params_name.index('P.M')])

        self._fig.add_trace(
            go.Heatmap(
                z = z_data,
                x = x_data,
                y = params_name,
                text = z_data_text,
                colorscale='Greys',
                # hoverinfo = 'x+text',
                hoverongaps = False,
                hovertemplate =
                    "%{y}[%{x}]<br>" +
                    "<b>%{text}</b><br>" +
                    "<extra></extra>"
            )
        )
        self._fig.update_layout(
            title='frame_of_patterns_ values<br>' + 'Line = ' + str(self._pos_line),
            xaxis_nticks = 50,
            xaxis = dict(
                rangeslider = dict(
                    visible = True,
                    thickness = 0.1,
                    yaxis = dict(
                        rangemode = "fixed",
                        range = [params_count - 2, params_count - 1]
                    )
                ),
                type="linear"
            )
        )
        self._fig.show()

if __name__ == "__main__":

    image_name = './/raccoon.jpg'
    image = cv2.imread(image_name, cv2.IMREAD_GRAYSCALE)
    assert image is not None, "No image in the path"
    image = image.astype(int)
    frame_of_patterns_ = cross_comp(image)  # returns Pm__

    visi_line = Visi_Line(
        image = image,
        frame_patterns = frame_of_patterns_,
        pos_line = 10
    )















