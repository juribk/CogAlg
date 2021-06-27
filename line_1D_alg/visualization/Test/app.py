import sys
import cv2

import dash
import dash_table
import pandas as pd


df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
)

if __name__ == '__main__':
    sys.path.append("../..")
    from line_patterns import cross_comp

    image_name = '..//..//.//raccoon.jpg'
    image_r = cv2.imread(image_name, cv2.IMREAD_GRAYSCALE)
    assert image_r is not None, "No image in the path"
    image_r = image_r.astype(int)
    frame_of_patterns_ = cross_comp(image_r)  # returns Pm__


    app.run_server(debug=True)