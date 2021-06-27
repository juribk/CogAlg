import numpy as np
import sys
import cv2
import json

import dash
import dash_table
from dash_table.Format import Format
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# TABLE STYLE ------------------------------------------------
table_header_style = {
    "backgroundColor": "rgb(2,21,70)",
    "color": "white",
    "textAlign": "center",
}
table_style_data_conditional = [
    # {
    #     "if": {"column_id": "param"},
    #     "textAlign": "right",
    #     "paddingRight": 10,
    # },
    {
        "if": {"row_index": "odd"},
        "backgroundColor": "white",
    },
]

# ------------------------------------------------------------


# Global variable
class visi_params():
    line_number = 0,
    img_type = 'ORIG',
    image_size = [0, 0]
    image_r = None
    image_p = None
    frame_of_patterns = None
    view = False

''' ---------------------------------------------------------------------------- '''

app = dash.Dash(
    __name__,
    external_stylesheets = [dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions = True,
)
server = app.server

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

app.layout = html.Div([
    html.Div(
        [
            html.Div([
                dcc.Graph(
                    id = 'src-image',
                    config = {
                        "modeBarButtonsToAdd": [
                            "drawline",
                        ]
                    },
                    style = {
                            "position": "relative",
                            "width": "100%",
                    },
                ),
            ]),
            html.Div([
                dcc.Slider(
                    id = 'img-slider',
                    min = 0,
                    step = 1,
                    ),
            ]),
            dbc.Card(
                [
                    dbc.CardHeader("Picture type"),
                    dbc.CardBody(
                        [
                            dcc.Dropdown(
                                id = 'select-type-image',
                                options = [
                                    {'label': 'Original', 'value': 'ORIG'},
                                    {'label': 'Patterns', 'value': 'PATR'},
                                ],
                                value = 'ORIG',
                                clearable = False
                            ),
                        ]
                    ),
                ]
            ),
            html.Br(),
            dbc.Card(
                [
                    dbc.CardHeader("Display items"),
                    dbc.CardBody(
                        [
                            dcc.Checklist(
                                id = "checklist-display-items",
                                options = [
                                    {'label': ' Source lines', 'value': 'S_SL'},
                                    {'label': ' Dert lines', 'value': 'S_DR'},
                                    {'label': ' Patterns lines', 'value': 'S_PL'},
                                ],
                                labelStyle = {"display": "block"},
                                value = ['S_SL', 'S_DR', 'S_PL']
                            )
                        ]
                    ),
                ]
            ),



            html.Div(id = 'test-text'),
        ],
        className = "side_bar",
    ),
    html.Div(
        [
            html.Div(
                [
                    html.Label(id = "lines-text-num", children= "Source. Line number = "),
                    dcc.Graph(
                        id = 'lines-source_image',
                        style = {"height": "200px"},
                    ),
                ],
                id = 'div-lines-source_image',
                className = "box",
            ),
            html.Div(
                [
                    html.Label("Dert"),
                    dcc.Graph(
                        id = 'lines-dert',
                        style = {"height": "200px"},
                    ),

                    dash_table.DataTable(
                        id = "dert-table",
                        virtualization=True,
                        style_header = table_header_style,
                        style_data_conditional = table_style_data_conditional,
                        fixed_rows = {'headers': True},
                        style_table = {'height': 300},
                        page_action = 'none',
                    )

                ],
                id = 'div-lines-source_dert',
                className = "box",
            ),
            html.Div(
                [
                    html.Label("Patterns"),
                    dcc.Graph(
                        id = 'lines-patterns',
                        style = {"height": "200px"},
                    ),
                ],
                id = 'div-lines-source_patterns',
                className = "box",
            ),
        ],
        className = "main",
    ),

])

# Callback Change Picture Type ---------------------------
@app.callback(
    dash.dependencies.Output('img-slider', 'max'),
    dash.dependencies.Output('img-slider', 'value'),
    dash.dependencies.Output('img-slider', 'marks'),
    [dash.dependencies.Input('select-type-image', 'value'),
     dash.dependencies.Input('src-image', 'clickData')]
)
def update_output(value, clickData):
    visi_params.img_type = value
    return visi_params.image_size[0], \
           clickData['points'][0]['y'] if clickData else 100, \
           {0: '0', str(visi_params.image_size[0]): str(visi_params.image_size[0])}

# Callback Change src-image Line --------------------------
@app.callback(
    dash.dependencies.Output('src-image', 'figure'),
    dash.dependencies.Output('lines-source_image', 'figure'),
    # dash.dependencies.Output('lines-dert', 'figure'),
    dash.dependencies.Output('lines-text-num', 'children'),
    [dash.dependencies.Input('img-slider', 'value')]
)
def update_output(value):
    visi_params.line_number = 2 if value < 2 else visi_params.image_size[0] - 3 if value > visi_params.image_size[0] - 3 else value
    if visi_params.img_type == 'ORIG':
        image = visi_params.image_r
    else:
        image = visi_params.image_p

    fig = px.imshow(
        img = image,
        binary_format = "png",
        color_continuous_scale = "Greys",
        binary_string = True
    )
    fig.update_layout(
        dragmode = "zoom",
        coloraxis_showscale = False,
        margin = dict(t = 10, r = 10, b = 10, l = 10),
    )
    fig.add_shape(
        type = 'line',
        x0 = 0,
        x1 = visi_params.image_size[1],
        y0 = visi_params.line_number,
        y1 = visi_params.line_number,
        xref = 'x',
        yref = 'y',
        line_color = 'red'
    )
    # fig.add_trace(
    #     go.Scatter(
    #         x = [0, visi_params.image_size[1]],
    #         y = [visi_params.line_number, visi_params.line_number],
    #         mode = "lines",
    #         line=go.scatter.Line(color = "red"),
    #         showlegend = False)
    # )
    return (
        fig,
        View_Source_Image(),
        # View_Dert_Image(fig),
       'Source. Line number = {}'.format(visi_params.line_number)
    )

# Callback When lines-source_image changed ----------------
@app.callback(
    Output('lines-dert', 'figure'),
    Output("dert-table", "columns"),
    Output("dert-table", "data"),
    Input('lines-source_image', 'relayoutData')
)
def display_reload_data(relayoutData):
    _range = None
    if relayoutData and visi_params.view:
        if 'xaxis.range[0]' in relayoutData:
            _range = [relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']]
        elif 'xaxis.range' in relayoutData:
            _range = relayoutData['xaxis.range']
    return View_Dert_Image(_range)

# Callback test checklist-display-items -------------------
@app.callback(
    Output('div-lines-source_image', 'style'),
    Output('div-lines-source_dert', 'style'),
    Output('div-lines-source_patterns', 'style'),
    [Input('checklist-display-items', 'value')]
)
def display_click_data(value):
    view_SL = {"display": "block" if 'S_SL' in value else "none"}
    view_DR = {"display": "block" if 'S_DR' in value else "none"}
    view_PL = {"display": "block" if 'S_PL' in value else "none"}
    return view_SL, view_DR, view_PL

# @app.callback(
#     Output('lines-dert', 'active_cell'),
#     Input('dert-table', 'clickData')
# )
# def display_click_data(value):
#     active_cell = {
#         "row": 310,
#         "column": 0,
#         # "row_id": df.country[row],
#         # "column_id": df.columns[column]
#     }
#     return active_cell


# Callback test clickData --------------------------------
# @app.callback(
#     Output('test-text', 'children'),
#     Input('lines-source_image', 'relayoutData'))
#     # Input('src-image', 'clickData'))
# def display_click_data(relayoutData):
#     return json.dumps(relayoutData, indent = 2)
#     # return json.dumps(clickData, indent = 2)

''' ---------------------------------------------------------------------------- '''
def Draw_Patterns_CP(image):
    img_out = np.zeros_like(image)
    for y, line in enumerate(visi_params.frame_of_patterns): # loop each y line
        x = 0
        for cp_pos, cp in enumerate(line): # loop each pattern
            x += cp.L
            img_out[y, x - 1] = 255
    # cv2.imwrite('.//assets/raccoon_p.jpg', img_out)
    return img_out
def Norm(_data):
    _window_min = np.nanmin(_data)
    _window_max = np.nanmax(_data)
    _data_norm = np.subtract(_data, _window_min)
    _div = (_window_max - _window_min) / 255
    _data_norm = np.divide(_data_norm, _div)
    return np.rint(_data_norm)
def Norm_Row(_data):
    _ret = np.zeros_like(_data)
    for _i, _row in enumerate(_data):
        _ret[_i] = Norm(_row)
    return np.rint(_ret)

# def View_Dert_Table(pos):
#     _colums_name = [
#        'Row',
#        'Original',
#        'dert.p',
#        'dert.d',
#        'dert.m',
#     ]
#     _table_columns = [{'id': _name, 'name': _name} for _name in _colums_name]
#     _table_data = np.full(len(visi_params.image_r[visi_params.line_number]), None)
#
#     _x_pos = 0
#     for pattern in visi_params.frame_of_patterns[visi_params.line_number]:  # loop each pattern
#         for x, dert in enumerate(pattern.dert_):
#             _pos = _x_pos + x
#             _z_data[_params_name.index('Original'), _pos] = visi_params.image_r[visi_params.line_number, _pos]
#             _z_data[_params_name.index('dert.p'), _pos] = dert.p
#             _z_data[_params_name.index('dert.d'), _pos] = dert.d
#             _z_data[_params_name.index('dert.m'), _pos] = dert.m
#
#             _data_row = _z_data[:, _pos]
#             _data_row = np.insert(_data_row, 0, _pos)
#             _table_data[_pos] = {_name: _z_data for _name, _z_data in zip(_colums_name, _data_row)}
#
#         _x_pos += pattern.L
#
#     return _table_columns, _table_data
#

# Viewing dert picture ----------------------------------
def View_Dert_Image(_range):
    _params_name = [
       'Original',             # List of displayed pramatras
       'dert.p',
       'dert.d',
       'dert.m',
    ]
    _colums_name = np.copy(_params_name)
    _colums_name = np.insert(_params_name, 0, 'Row')
    _table_columns = [{'id': _name, 'name': _name} for _name in _colums_name]

    # _params_name.reverse()
    _params_count = len(_params_name)
    _x_data = np.arange(len(visi_params.image_r[visi_params.line_number]))
    _z_data = np.full((len(_params_name), len(visi_params.image_r[visi_params.line_number])), np.NAN)
    _table_data = np.full(len(visi_params.image_r[visi_params.line_number]), None)

    # _z_data[_params_name.index('Original')] = visi_params.image_r[visi_params.line_number]
    _x_pos = 0
    # print(visi_params.line_number)
    for pattern in visi_params.frame_of_patterns[visi_params.line_number]:  # loop each pattern
        for x, dert in enumerate(pattern.dert_):
            _pos = _x_pos + x
            _z_data[_params_name.index('Original'), _pos] = visi_params.image_r[visi_params.line_number, _pos]
            _z_data[_params_name.index('dert.p'), _pos] = dert.p
            _z_data[_params_name.index('dert.d'), _pos] = dert.d
            _z_data[_params_name.index('dert.m'), _pos] = dert.m

            _data_row = _z_data[:, _pos]
            _data_row = np.insert(_data_row, 0, _pos)
            _table_data[_pos] = {_name: _z_data for _name, _z_data in zip(_colums_name, _data_row)}

        _x_pos += pattern.L

    _fig = go.Figure()
    _fig.add_trace(
        go.Heatmap(
            z = Norm_Row(_z_data[::-1]),
            x = _x_data,
            y = _params_name[::-1],
            text = _z_data[::-1],
            colorscale = 'Greys',
            showscale = False,
            reversescale = True,
            hoverongaps = False,
            hovertemplate =
                "%{y}[%{x}]<br>" +
                "<b>%{text}</b><br>" +
                "<extra></extra>"
        )
    )
    _fig.update_layout(
        margin = dict(t = 10, r = 25, b = 10, l = 70),
        xaxis_nticks = 50,
    )
    if _range:
        _fig.update_xaxes(range = _range)

    return _fig, _table_columns, _table_data

# Viewing multiple lines of a picture -------------------
def View_Source_Image():
    _params_name = [
        'Line -2',                  # List of displayed pramatras
        'Line -1',
        'Line 00',
        'Line +1',
        'Line +2',
    ]
    _params_name.reverse()
    _params_count = len(_params_name)

    _x_data = np.arange(len(visi_params.image_r[visi_params.line_number]))
    _z_data = np.full((len(_params_name), len(visi_params.image_r[visi_params.line_number])), np.NAN)
    for _line, _name in enumerate(_params_name, start = visi_params.line_number - 2):
        _z_data[_params_name.index(_name)] = visi_params.image_r[_line]

    _fig = go.Figure()
    _fig.add_trace(
        go.Heatmap(
            z = _z_data,
            x = _x_data,
            y = _params_name,
            text = _z_data,
            colorscale = 'Greys',
            showscale = False,
            reversescale = True,
            hoverongaps = False,
            hovertemplate =
                "%{y}[%{x}]<br>" +
                "<b>%{text}</b><br>" +
                "<extra></extra>"
        )
    )
    _fig.update_layout(
        # title='frame_of_patterns_ values<br>' + 'Line = ' + str(visi_params.line_number),
        margin = dict(t = 10, r = 25, b = 10, l = 70),
        xaxis_nticks = 50,
        xaxis = dict(
            rangeslider = dict(
                visible = True,
                thickness = 0.1,
                # yaxis = dict(
                #     rangemode = "fixed",
                #     range = [1, params_count - 2]
                # )
            ),
            # type = "linear"
        )
    )
    # _fig.update_layout(clickmode = 'event+select')
    # _fig.update_xaxes(range = [100, 500])
    return _fig

if __name__ == '__main__':

    sys.path.append("..")
    from line_patterns import cross_comp

    image_name = '..//raccoon.jpg'
    image_r = cv2.imread(image_name, cv2.IMREAD_GRAYSCALE)
    assert image_r is not None, "No image in the path"
    image_r = image_r.astype(int)
    frame_of_patterns_ = cross_comp(image_r)  # returns Pm__


    visi_params.frame_of_patterns = frame_of_patterns_
    image_p = Draw_Patterns_CP(image_r)
    visi_params.image_size = image_p.shape
    visi_params.image_r = image_r
    visi_params.image_p = image_p
    visi_params.line_number = 0
    visi_params.view = True

    app.run_server(debug = True)