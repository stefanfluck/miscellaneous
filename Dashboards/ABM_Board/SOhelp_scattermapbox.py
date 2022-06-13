# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 11:00:07 2022

@author: fluf
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

app = dash.Dash()
server = app.server

np.random.seed(0)
# Random dummy data
n = 100
time = np.linspace(0, 1, n)
latitude = 50 + 0.001 * np.cumsum(np.random.randn(n))
longitude = 2 + 0.001 * np.cumsum(np.random.randn(n))
altitude = (time - 0.5) ** 2
heartrate = 100 + np.cumsum(np.random.randn(n))
df = pd.DataFrame(
    {
        "time": time,
        "latitude": latitude,
        "longitude": longitude,
        "altitude": altitude,
        "heartrate": heartrate,
    }
)



fig = go.Figure(go.Scattermapbox(
    mode = "markers+lines",
    lon = df.longitude,
    lat = df.latitude,
    marker = {'size': 10}))
fig.update_layout(
    mapbox={
        'style': "open-street-map",
        'center' : dict(
            lat=50,
            lon=2
        ),
        'zoom': 12})


app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Graph(id="mymap", figure=fig),
            ]
        ),
        html.Div(
            [
                dcc.Graph(id="time-series"),
                dcc.Dropdown(
                    id="column",
                    options=[
                        {"label": i, "value": i} for i in ["altitude", "heartrate"]
                    ],
                    value="altitude",
                ),
            ]
        ),
    ]
)


def lineplot(x, y, title="", axis_type="Linear"):
    return {
        "data": [go.Scatter(x=x, y=y, mode="lines")],
    }


@app.callback(
    Output("time-series", "figure"),
    [
        Input("column", "value"),
        Input("mymap", "selectedData")
    ],
)
def update_timeseries(column, selectedData):
    # add filter data by selectData points
    temp = df
    if selectedData is not None:
        sel_data = pd.DataFrame(selectedData['points'])
        temp = df.loc[(df.latitude.isin(sel_data.lat)) & (df.longitude.isin(sel_data.lon))]
    x = temp["time"]
    y = temp[column]
    return lineplot(x, y)


app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})


if __name__ == "__main__":
    app.run_server()
