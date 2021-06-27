"""

"""

import sys
import numpy as np
import datetime
import plotly.graph_objects as go

import cv2

class Visi_Line(object):
    """

    """

    def __init__(self, data1, data2, names):
        """ Constructor """
        self.data1 = data1
        self.data2 = data2
        self.names = names

    def visi(self):
        """ Отобразим данные """

        return 0



if __name__ == "__main__":

    image_name = './/raccoon.jpg'
    image_c = cv2.imread(image_name, cv2.IMREAD_COLOR)


    # visi = Visi_Line("blue", 5, 4, "car")
    # visi.visi()

    # # Create figure
    # fig = go.Figure()
    #
    # # Add traces, one for each slider step
    # for step in np.arange(0, 5, 0.1):
    #     fig.add_trace(
    #         go.Scatter(
    #             visible=False,
    #             line=dict(color="#00CED1", width=6),
    #             name="𝜈 = " + str(step),
    #             x=np.arange(0, 10, 0.01),
    #             y=np.sin(step * np.arange(0, 10, 0.01))
    #         )
    #     )
    #
    # # Make 10th trace visible
    # fig.data[10].visible = True
    #
    # # Create and add slider
    # steps = []
    # for i in range(len(fig.data)):
    #     step = dict(
    #         method="update",
    #         args=[{"visible": [False] * len(fig.data)},
    #               {"title": "Slider switched to step: " + str(i)}],  # layout attribute
    #     )
    #     step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
    #     steps.append(step)
    #
    # sliders = [dict(
    #     active=10,
    #     currentvalue={"prefix": "Frequency: "},
    #     pad={"t": 50},
    #     steps=steps
    # )]
    #
    # fig.update_layout(
    #     sliders=sliders
    # )
    #
    # fig.show()



    np.random.seed(1)

    programmers = ['Alex','Nicole','Sara','Etienne','Chelsea','Jody','Marianne']

    base = datetime.datetime.today()
    dates = base - np.arange(180) * datetime.timedelta(days=1)
    z = np.random.poisson(size=(len(programmers), len(dates)))

    fig = go.Figure()

    fig.add_trace(
        go.Heatmap(
            z=z,
            x=dates,
            y=programmers,
            text=z,
            colorscale='Greys')
    )

    # fig = go.Figure(data=go.Heatmap(
    #         z=z,
    #         x=dates,
    #         y=programmers,
    #         text = z,
    #         colorscale='Greys'))

    fig.update_layout(
        title='GitHub commits per day',
        xaxis_nticks=36,

        xaxis = dict(
            rangeslider=dict(
                visible=True,
                thickness = 0.1,
                yaxis = dict(
                    rangemode = "fixed",
                    range = [0, 1]
                )
            ),
            type="date"
        )
    )

    fig.show()



    # import plotly.graph_objects as go
    #
    # import pandas as pd
    #
    # # Load data
    # df = pd.read_csv(
    #     "https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv")
    # df.columns = [col.replace("AAPL.", "") for col in df.columns]
    #
    # # Create figure
    # fig = go.Figure()
    #
    # fig.add_trace(
    #     go.Scatter(x=list(df.Date), y=list(df.High)))
    #
    # # Set title
    # fig.update_layout(
    #     title_text="Time series with range slider and selectors"
    # )
    #
    # # Add range slider
    # fig.update_layout(
    #     xaxis=dict(
    #         rangeslider=dict(
    #             visible=True
    #         ),
    #         type="date"
    #     )
    # )
    #
    # fig.show()