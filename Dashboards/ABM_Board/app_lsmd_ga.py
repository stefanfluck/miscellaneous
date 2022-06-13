"""
Dashboard app to display Go Arounds in Duebendorf LSMD airport.


"""

# %%import modles and classes from other file
from classes_GAgen import *

from airtraj import trajectories as traj
from os import path
import pickle
from traffic.data import airports
import matplotlib.pyplot as plt
import pandas as pd

import plotly.graph_objects as go
import plotly.offline as pyo
import plotly.express as px

import numpy as np
import assets.dashboard_tools as dashboard

#%% functions

# lv03->wgs84 vgl https://www.swisstopo.admin.ch/content/swisstopo-internet/en/
# online/calculation-services/_jcr_content/contentPar/tabs/items/
# documents_publicatio/tabPar/downloadlist/downloadItems/
# 19_1467104393233.download/ch1903wgs84_e.pdf


#%% bounds
# lon_bounds = [8.50, 8.76]
# lat_bounds = [47.35, 47.44]
# lat_bounds[1] += 0.05
sgx_bounds = [680000, 699800]
sgy_bounds = [245000, 254800]
alt_bounds = [609, 2407]

altinislider_params = {"min": 1450, "max": 5000, "default": 2000}
altlvlslider_params = {"min": 2000, "max": 8000, "default": 5000}
gspclislider_params = {"min": 100, "max": 300, "default": 150}
gsplvlslider_params = {"min": 50, "max": 400, "default": 200}
rocclislider_params = {"min": 300, "max": 3500, "default": 2700}

data_dir = r"assets/"
# %% Load kde fitted
with open(path.join(data_dir, "kde_fitted_no_tol.pkl"), "rb") as handle:
    kde_dict = pickle.load(handle)

with open(path.join(data_dir, "smoothed_kde_levels.pickle"), "rb") as handle:
    kde_levels_xarray = pickle.load(handle)

kde_levels_xarray = kde_levels_xarray.sel(
    AltitudeBaro=slice(3000, 8000)
)  # stuff below 3km is boring

fig_smoothed = px.imshow(
    kde_levels_xarray.T,
    animation_frame="AltitudeBaro",
    # color_continuous_scale="RdBu_r",
    color_continuous_scale="Hot_r",
    zmin=1e-13,
    zmax=1e-10,
    origin="lower",
    # binary_string='True',
    #                          zmin=0,
    #                          zmax=np.max(tmp_smooth.values)
)
fig_smoothed.update_layout(plot_bgcolor="rgba(241, 241, 241, 0)")
fig_smoothed.update_yaxes(
    scaleanchor="x",
    scaleratio=1,
)

#%% import traj of LSMD GAs# open the file

df_ga_lsmd = dashboard.load_ga_lsmd(data_dir)

#%% import traj of LSZH RWY14 GAs

df_ga_lszh14_spatfilt = dashboard.load_ga_lszh(data_dir)

#%% import csv's with GA from dub, teterboro, lcy

df_kt06_dub = pd.read_csv(data_dir+'\df_kt06_dub.csv')
df_kt19_dub = pd.read_csv(data_dir+'\df_kt19_dub.csv')
df_lcy_dub = pd.read_csv(data_dir+'\df_lcy_dub.csv')


#%% load ga lszh14 heatmap image array

with open(path.join(data_dir, "ga_path_kde.pkl"), "rb") as handle:
    ga_kde_path = pickle.load(handle)

distance_m = ga_kde_path["distance_m"]
alts_m = ga_kde_path["alts_m"]
pdf_grid = ga_kde_path["pdf_grid"]


#%% dash app
from dash import Dash, html, dcc, Input, Output

app = Dash(
    __name__,
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
)
server = app.server
app.title = "LSMD GA Inspector"

# -- initial figures ----------------------------------------------------------

# # trajs lsmd and lszh14 figure
# fig = go.Figure(layout=go.Layout(plot_bgcolor="rgba(241, 241, 241, 0.8)"))

# # fig_lszh = px.line_mapbox(
# #     df_ga_lszh14_spatfilt, lat="Lat", lon="Lon", line_group="ID"
# # )
# # fig_lszh.update_traces(line=dict(color="darkblue", width=0.5))
# # fig_lszh.update_layout(mapbox_style="carto-positron")

# fig_lszh = px.density_mapbox(
#     df_ga_lszh14_spatfilt,
#     lat="Lat",
#     lon="Lon",
#     radius=5,
#     center=dict(lat=47.35, lon=8.66),
#     zoom=11,
#     color_continuous_scale="Hot_r",
#     range_color=[0, 10],
#     mapbox_style="carto-positron",
# )
# fig_lszh.update_layout(coloraxis_showscale=False)

# fig_lsmd = px.line_mapbox(df_ga_lsmd, lat="Lat", lon="Lon", line_group="ID")
# fig_lsmd.update_layout(mapbox_style="carto-positron")
# fig_lsmd.update_traces(line=dict(color="black", width=0.5))
# for traces in fig_lsmd.data:
#     fig_lszh.add_traces(traces)
# fig = fig_lszh

# zoom, center = dashboard.zoom_center(
#     tuple(df_ga_lszh14_spatfilt["Lon"]) + tuple(df_ga_lsmd["Lon"]),
#     tuple(df_ga_lszh14_spatfilt["Lat"]) + tuple(df_ga_lsmd["Lat"]),
# )
# center["lon"] += 0.05
# center["lat"] -= 0.05
# fig.update_layout(mapbox=dict(center=center, zoom=zoom - 0.5))

# fig.update_layout(
#     margin={"r": 20, "t": 20, "l": 20, "b": 20},
# )


"""
performance workaround ideas:
    put all the traces together to one df and add one na line to it at end
"""


# --- emtpy 3d scatterplot ----------------------------------------------------

# scatter_start_df = pd.DataFrame()
# sctplt = go.Figure(layout=go.Layout(plot_bgcolor='rgba(241, 241, 241, 0.8)'))
# sct = go.Figure(data=[go.Scatter3d(x=[0], y=[0], z=[0], mode="markers")])
# fig_smoothed.update_layout(width=800)
fig_smoothed.update_layout(height=500)
fig_smoothed.update_layout(
    margin={"r": 20, "t": 20, "l": 20, "b": 20},
    # yaxis_range=[2000, 7800],
    xaxis_range=[680000, 700000],
)

# --- layout of the app -----------------------------------------------------------------------------

app.layout = html.Div(
    [
        html.Img(
            src="assets/zhaw.png", style={"float": "right", "height": "120px"}
        ),
        html.H1(children="Go Arounds Duebendorf (LSMD) and Zurich (LSZH)"),
        html.P(
            children="(c) ZHAW Center for Aviation, with data by OpenSky Network."
        ),
        html.Div([html.Hr()]),  # separation line
        # first section
        html.Div(
            [
                html.H2(children="Problem Statement"),
                dcc.Markdown(
                    children="In this dashboard you can visualize **Go Arounds from "
                    "Zurich (LSZH) and Duebendorf (LSMD)**. "
                    "Due to the closeness of these airports, simulataneous Go-Arounds at both airports could lead to situations, where the probability"
                    " for a collision approaches the Target Level of Safety (TLS) because the procedures are flown not as precisely as designed."
                    " This dashboard allows to **visualize** the flown Go-Arounds at both airfields in the **first section**. In the **second section**, a "
                    "synthetic Go-Around can be generated by modifying the sliders. A **vertical profile** of the generated Go-Around is then displayed"
                    " on a heatmap, which shows the probability of having aircraft going around at LSZH along the RWY heading of LSMD RWY29. "
                    "Based on the chosen Go-Around, the **probability for a collision is calculated**, assuming there are simultaneous Go-Arounds at LSZH RWY14 "
                    "and LSMD RWY29. To calculate real collision probabilities, however, the probability of having simulataneous Go-Arounds also needs to be "
                    "factored in. This probability is dependent on various factors, which can be selected in the **third section**. The **final collision probabilities** "
                    "are then displayed in red at the top of the third section for each calculation method.",
                    style={"margin-bottom": "30px"},
                ),
                html.Div(
                    [
                        html.Div(
                            [  # left column of first section
                                html.H4(children="Go-Arounds Overview"),
                                dcc.Markdown(
                                    children="The following figure shows Go-Around Trajectories from LSMD RWY29 in black. The Go-Arounds from LSZH RWY14"
                                    " can either be displayed as a heatmap or discrete trajectories (Caution: lines take longer to load!)."
                                ),
                                dcc.RadioItems(id = 'traj-checklist',
                                    options={
                                        'dens':'Density',
                                        'lines':'Trajectories',
                                        },
                                    value='dens',
                                    inline=True,
                                    inputStyle={"margin-left": "30px"}),
                                dcc.Graph(id="ga-trajs"),
                            ],
                            className="six columns",
                        ),
                        html.Div(
                            [  # right column of first section
                                html.H4("GA LSZH RWY14 Density by Altitude"),
                                dcc.Markdown(
                                    children="This plot shows the density of GA trajectories filtered by a specific altitude "
                                    "from LSZH RWY14. Select a different altitude with the slider below the figure."
                                ),
                                dcc.Graph(
                                    id="speed_dist", figure=fig_smoothed
                                ),
                                html.Pre(id="ga-3d"),
                            ],
                            className="six columns",
                        ),
                    ],
                    className="row",
                ),
            ]
        ),
        html.Div([html.Hr()]),  # horizontal separator line
        # second section
        html.Div(
            [
                html.H2(children="Generate Synthetic GA"),
                html.P(
                    children="Generate a synthetic GA by selecting values with "
                    "the sliders on the left hand side. "
                    "The generated GA is then displayed on the right as a black line overlaid "
                    "over a probabilty map of Go-Arounds from LSZH RWY14. The colored areas represent areas where Go-Arounds from LSZH pierce a plane along"
                    "the runway axis of LSMD RWY29. The green squares "
                    "represent observed Go-Around trajectories from LSMD (only along RWY axis). "
                    "A worst-case, real GA is set as default.",
                    style={"margin-bottom": "30px"},
                ),
                html.Div(
                    [
                        # left column, second section
                        html.Div(
                            [
                                html.H4(children="Parameter Selection"),
                                # dcc.Graph(id='ga-trajs2', figure=fig),
                                # altini slider
                                dcc.Markdown(
                                    children="**GA Initiation Altitude:**"
                                    " Select the altitude at which the GA in LSMD will "
                                    "be initiated.",
                                    style={"margin-top": "20px"},
                                ),
                                dcc.Slider(
                                    id="altini-slider",  # select values above
                                    min=altinislider_params["min"],
                                    max=altinislider_params["max"],
                                    step=50,
                                    value=altinislider_params["default"],
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                    marks={
                                        altinislider_params["min"]: str(
                                            altinislider_params["min"]
                                        )
                                        + " ft",
                                        altinislider_params["default"]: str(
                                            altinislider_params["default"]
                                        ),
                                        altinislider_params["max"]: str(
                                            altinislider_params["max"]
                                        )
                                        + " ft",
                                    },
                                    included=False,
                                ),
                                # gspcli slider
                                dcc.Markdown(
                                    children="**Groundspeed during Climb:**"
                                    " Select the speed at which the climb phase of the "
                                    "GA is flown.",
                                    style={"margin-top": "20px"},
                                ),
                                dcc.Slider(
                                    id="gspcli-slider",  # select values above
                                    min=gspclislider_params["min"],
                                    max=gspclislider_params["max"],
                                    step=10,
                                    value=gspclislider_params["default"],
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                    marks={
                                        gspclislider_params["min"]: str(
                                            gspclislider_params["min"]
                                        )
                                        + " kts",
                                        gspclislider_params["default"]: str(
                                            gspclislider_params["default"]
                                        ),
                                        gspclislider_params["max"]: str(
                                            gspclislider_params["max"]
                                        )
                                        + " kts",
                                    },
                                    included=False,
                                ),
                                # roccli slider
                                dcc.Markdown(
                                    children="**Rate of Climb:** Select the ROC at "
                                    "which the GA is flown.",
                                    style={"margin-top": "20px"},
                                ),
                                dcc.Slider(
                                    id="roccli-slider",  # select values above
                                    min=rocclislider_params["min"],
                                    max=rocclislider_params["max"],
                                    step=100,
                                    value=rocclislider_params["default"],
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                    marks={
                                        rocclislider_params["min"]: str(
                                            rocclislider_params["min"]
                                        )
                                        + " ft/min",
                                        rocclislider_params["default"]: str(
                                            rocclislider_params["default"]
                                        ),
                                        rocclislider_params["max"]: str(
                                            rocclislider_params["max"]
                                        )
                                        + " ft/min",
                                    },
                                    included=False,
                                ),
                                # altlvl slider
                                dcc.Markdown(
                                    children="**Level-Off Altitude:**"
                                    " Select the altitude at which the level-off occurs.",
                                    style={"margin-top": "20px"},
                                ),
                                dcc.Slider(
                                    id="altlvl-slider",  # select values above
                                    min=altlvlslider_params["min"],
                                    max=altlvlslider_params["max"],
                                    step=1000,
                                    value=altlvlslider_params["default"],
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                    marks={
                                        altlvlslider_params["min"]: str(
                                            altlvlslider_params["min"]
                                        )
                                        + " ft",
                                        altlvlslider_params["default"]: str(
                                            altlvlslider_params["default"]
                                        ),
                                        altlvlslider_params["max"]: str(
                                            altlvlslider_params["max"]
                                        )
                                        + " ft",
                                    },
                                    included=False,
                                ),
                                # gsplvl slider
                                dcc.Markdown(
                                    children="**Groundspeed after Level-Off:**"
                                    " Select the speed at which the GA is flown after "
                                    "level-off.",
                                    style={"margin-top": "20px"},
                                ),
                                dcc.Slider(
                                    id="gsplvl-slider",  # select values above
                                    min=gsplvlslider_params["min"],
                                    max=gsplvlslider_params["max"],
                                    step=10,
                                    value=gsplvlslider_params["default"],
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                    marks={
                                        gsplvlslider_params["min"]: str(
                                            gsplvlslider_params["min"]
                                        )
                                        + " kts",
                                        gsplvlslider_params["default"]: str(
                                            gsplvlslider_params["default"]
                                        ),
                                        gsplvlslider_params["max"]: str(
                                            gsplvlslider_params["max"]
                                        )
                                        + " kts",
                                    },
                                    included=False,
                                ),
                                # store value for calculated probability smlt ga data
                                dcc.Store(id="probability-simlt-ga-data"),
                                dcc.Markdown(
                                    "**Probability for a Collision with the generated GA**",
                                    # given that there is a GA in LSZH and in LSMD at the same time (P=1). "
                                    # "To get real probability values, these values need to be multiplied by the probability of having "
                                    # "simultaneous GA at both airports (see next section)",
                                    style={"margin-top": "50px"},
                                ),
                                html.P(
                                    id="probability-simlt-ga",
                                    children="NIL",
                                    style={
                                        "fontSize": 18,
                                        "color": "red",
                                        "text-align": "left",
                                    },
                                ),
                                dcc.Markdown(
                                    "**Comparison Values** from other Airports: ",
                                    style={"margin-top": "20px"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.P(
                                                    children="London City GA:",
                                                    style={
                                                        "fontSize": 14,
                                                        "color": "black",
                                                        "text-align": "left",
                                                    },
                                                ),
                                            ],
                                            className="four columns",
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    id="probability-lcy",
                                                    children="6.0e-7 x Prob. of having simultaneous GAs",
                                                    style={
                                                        "fontSize": 14,
                                                        "color": "red",
                                                        "text-align": "left",
                                                    },
                                                ),
                                            ],
                                            className="eight columms",
                                        ),
                                    ],
                                    className="row",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.P(
                                                    children="Teterboro RWY06 GA:",
                                                    style={
                                                        "fontSize": 14,
                                                        "color": "black",
                                                        "text-align": "left",
                                                    },
                                                ),
                                            ],
                                            className="four columns",
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    id="t06-lcy",
                                                    children="2.4e-6 x Prob. of having simultaneous GAs",
                                                    style={
                                                        "fontSize": 14,
                                                        "color": "red",
                                                        "text-align": "left",
                                                    },
                                                ),
                                            ],
                                            className="eight columms",
                                        ),
                                    ],
                                    className="row",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.P(
                                                    children="Teterboro RWY19 GA:",
                                                    style={
                                                        "fontSize": 14,
                                                        "color": "black",
                                                        "text-align": "left",
                                                    },
                                                ),
                                            ],
                                            className="four columns",
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    id="t19-lcy",
                                                    children="1.6e-6 x Prob. of having simultaneous GAs",
                                                    style={
                                                        "fontSize": 14,
                                                        "color": "red",
                                                        "text-align": "left",
                                                    },
                                                ),
                                            ],
                                            className="eight columms",
                                        ),
                                    ],
                                    className="row",
                                ),
                                # dcc.RangeSlider(id='altini-slider', value=[5,15], min=0, max=20, marks=None),
                            ],
                            className="five columns",
                        ),
                        # right column of second section
                        html.Div(
                            [
                                html.H4("Go-Around Visualization"),
                                dcc.Markdown('Select observed Go-Arounds at LSMD or generated Go-Arounds with performance data from other airports'
                                             ' to plot in the vertical crosssection:',
                                             style={"margin-top": "20px"}),
                                dcc.Checklist(
                                    id = 'ga-checklist',
                                    options={
                                        'dub29':'Duebendorf observed GA RWY29',
                                        'tet06':'Teterboro RWY06',
                                        'tet19':'Teterboro RWY19',
                                        'lcy27':'London City RWY27',
                                        },
                                    value=[],
                                    inline=True,
                                    inputStyle={"margin-left": "30px"}),
                                
                                dcc.Graph(id="ga-heatmap"),
                            ],
                            className="seven columns",
                        ),
                    ],
                    className="row",
                ),
            ]
        ),
        html.Div([html.Hr()]),  # horizontal separator line
        # third section
        html.Div(
            [
                html.H2(
                    children="Simultaneous Go Arounds Probability",
                    style={"margin-top": "30px"},
                ),
                html.P(
                    children="In this section, two methods for computing the probability of simultaneous go-arounds are used",
                    style={"margin-bottom": "20px"},
                ),
                html.Div(
                    [
                        # left column
                        html.Div(
                            [
                                html.H4(children="Conditional Method"),
                                html.P(
                                    "This method methods use conditional probabilities in order to estimate the probability of simultaneous Go-Arounds per landing in Duebendorf."
                                ),
                                dcc.Markdown(
                                    "**GA rate in LSMD**: Enter a number for the rate per"
                                    " 1000 landings that is a GA in Duebendorf.",
                                    style={"margin-top": "20px"},
                                ),
                                dcc.Input(
                                    id="rategadub-inpt",
                                    type="number",
                                    placeholder=4,
                                    value=4,
                                    min=0,
                                    max=1000,
                                    debounce=True,
                                ),
                                dcc.Markdown(
                                    "**Probabilty of GA in LSZH when GA in LSMD**: Enter "
                                    "a number for the probability that there is also a "
                                    "GA in Zurich when there is a GA in Duebendorf.",
                                    style={"margin-top": "20px"},
                                ),
                                dcc.Input(
                                    id="pagazwhengadub-inpt",
                                    type="number",
                                    min=0,
                                    max=1,
                                    placeholder=0.1,
                                    value=0.1,
                                    debounce=True,
                                ),
                                dcc.Markdown(
                                    "**Probability of simultaneous Go-Arounds:**",
                                    style={"margin-top": "20px"},
                                ),
                                html.P(
                                    id="prob-result-sim_ga",
                                    children="NIL",
                                    style={
                                        "fontSize": 24,
                                        "color": "red",
                                        "text-align": "left",
                                    },
                                ),
                                dcc.Markdown(
                                    "**Probability of Collision per landing in Duebendorf:**",
                                    style={"margin-top": "20px"},
                                ),
                                html.P(
                                    id="prob-result-method1",
                                    children="NIL",
                                    style={
                                        "fontSize": 24,
                                        "color": "red",
                                        "text-align": "left",
                                    },
                                ),
                            ],
                            className="six columns",
                        ),
                        # right column
                        html.Div(
                            [
                                html.H4("Correlation Method"),
                                html.P(
                                    "This method use correlation factor to compute the probability of simultanous Go-Arounds per landing in Duebendorf."
                                ),
                                dcc.Markdown(
                                    "**GA rate in LSMD**: Enter a number for the rate per"
                                    " 1000 landings that is a GA in Duebendorf.",
                                    style={"margin-top": "20px"},
                                ),
                                dcc.Input(
                                    id="rategadub-2-inpt",
                                    type="number",
                                    placeholder=4,
                                    value=4,
                                    min=0,
                                    max=1000,
                                    debounce=True,
                                ),
                                dcc.Markdown(
                                    "**GA rate in LSZH RWY14**: Enter a number for the rate per"
                                    " 1000 landings that is a GA at LSZH RWY 14.",
                                    style={"margin-top": "20px"},
                                ),
                                dcc.Input(
                                    id="rategazue14-inpt",
                                    type="number",
                                    placeholder=4,
                                    value=2,
                                    min=0,
                                    max=1000,
                                    debounce=True,
                                ),
                                dcc.Markdown(
                                    "**Correlation Factor**: Enter a number for a correlation factor that links GA in Duebendorf and Zuerich.",
                                    style={"margin-top": "20px"},
                                ),
                                dcc.Input(
                                    id="rho-inpt",
                                    type="number",
                                    placeholder=0.1,
                                    value=0.1,
                                    min=0,
                                    max=1,
                                    debounce=True,
                                ),
                                dcc.Markdown(
                                    "**Probability of Landing in LSZH if Landing in "
                                    "LSMD**: Enter a number for the probability that "
                                    "there is also a landing in Zurich when there is a "
                                    "landing in Duebendorf",
                                    style={"margin-top": "20px"},
                                ),
                                dcc.Input(
                                    id="plndzwhenlnddue-inpt",
                                    type="number",
                                    placeholder=1,
                                    value=1,
                                    debounce=True,
                                ),
                                dcc.Markdown(
                                    "The selection of the above parameters yields a **Probability of a GA in LSZH when theres a GA in LSMD** (comparable with second input of Method 1) of:",
                                    style={"margin-top": "20px"},
                                ),
                                ####
                                dcc.Markdown(
                                    "**Probability of simultaneous Go-Arounds:**",
                                    style={"margin-top": "20px"},
                                ),
                                html.P(
                                    id="p_ga_dub_and_ga14_dep",
                                    children="NIL",
                                    style={
                                        "fontSize": 24,
                                        "color": "red",
                                        "text-align": "left",
                                    },
                                ),
                                dcc.Markdown(
                                    "**Probability of Collision per landing in Duebendorf:**",
                                    style={"margin-top": "20px"},
                                ),
                                html.P(
                                    id="prob-result-method2",
                                    children="NIL",
                                    style={
                                        "fontSize": 24,
                                        "color": "red",
                                        "text-align": "left",
                                    },
                                ),
                            ],
                            className="six columns",
                        ),
                    ],
                    className="row",
                ),
            ]
        ),
    ],
    style={
        "margin-left": "75px",
        "margin-right": "75px",
        "margin-top": "50px",
        "margin-bottom": "50px",
    },
)


# --- functions to update figure


"""
filter df by selectedData and get subset of it
"""


@app.callback(
    Output("ga-heatmap", "figure"),
    [
        Input("altini-slider", "value"),
        Input("altlvl-slider", "value"),
        Input("gspcli-slider", "value"),
        Input("roccli-slider", "value"),
        Input("gsplvl-slider", "value"),
        Input("ga-checklist", "value"),
    ],
)
def update_ga_heatmap_graph(altini, altlvl, gspcli, roccli, gsplvl, gachecklist):

    # generate trajectory to plot

    # gsplvl = 200  # Does not have impact on proba col. implemented as slider again

    # create ga_traj_gen object and generate a trajectory

    ga_lsmd = GaTrajGen(
        airport="LSMD",
        runway=29,
        glideslope=4.5,
        boundaries=[
            min(sgx_bounds),
            min(sgy_bounds),
            max(sgx_bounds),
            max(sgy_bounds),
        ],
    )

    # generate a few example trajectories
    ga_traj = ga_lsmd.generate_ga(
        alt_ini=altini,
        alt_lvl=altlvl,
        gsp_cli=gspcli,
        gsp_lvl=gsplvl,
        roc_cli=roccli,
        dt=3,
    )
    ga_traj["distance"] = ga_lsmd.get_dist_from_point(
        ga_traj["SwissGridX"].values, ga_traj["SwissGridY"].values
    )

    # plot contourf
    fig = go.Figure(
        data=go.Contour(
            z=pdf_grid.T,
            y=alts_m * (1 / 0.3048),  # horizontal axis
            x=distance_m,  # vertical axis
            colorscale="Hot_r",
            colorbar=dict(
                title="Prob. for Collision",
                # titleside="top",
                # tickmode="array",
                # tickvals=[1e-15, 1e-12, 1e-10],
                # ticktext=["Cool", "Mild", "Hot"],
                ticks="outside",
                tickformat="%e",
            ),
            opacity=0.95,
            name='GA LSZH RWY14 piercing through',
        ),
        layout=go.Layout(
            plot_bgcolor="rgba(241, 241, 241, 0)",
            xaxis=dict(
                title="Distance along go-around path in meter", dtick=1500
            ),
            yaxis=dict(title="Altitude in ft"),
            xaxis_tickformat="%d",
            hovermode="closest",
        ),
    )




    fig.add_trace(
        go.Scatter(
            x=ga_traj["distance"],
            y=ga_traj["Altitude[ft]"],
            mode="lines+markers",
            marker=dict(
                size=6,
                color="black",
                symbol="line-ns",
                line=dict(width=0.75, color="black"),
            ),
            showlegend=False,
            name='Synthetic GA'
        ),
    )
    


    if 'tet06' in gachecklist:
        fig.add_trace(
                go.Histogram2dContour(
                            x=df_kt06_dub['distance'],
                            y=df_kt06_dub['Alt'],
                            name="Teter. RWY06",
                            ncontours=5,
                            colorscale = ['rgba(0, 0, 255, 0)', 
                                          'rgba(255, 255, 0, 0.05)', 
                                           'rgba(255, 255, 0, 0.1)'],
                            reversescale=False,
                            showscale=False,
                            opacity=1,
                            )
            )

    if 'tet19' in gachecklist:
        fig.add_trace(
                go.Histogram2dContour(
                            x=df_kt19_dub['distance'],
                            y=df_kt19_dub['Alt'],
                            name="Teter. RWY19",
                            ncontours=5,
                            colorscale = ['rgba(0, 0, 255, 0)', 
                                          'rgba(0, 0, 255, 0.05)', 
                                           'rgba(0, 0, 255, 0.1)'],
                            reversescale=False,
                            showscale=False,
                            opacity=1,
                            )
            )

    if 'lcy27' in gachecklist:
        fig.add_trace(
                go.Histogram2dContour(
                            x=df_lcy_dub['distance'],
                            y=df_lcy_dub['Alt'],
                            name="LCY RWY27",
                            ncontours=5,
                            colorscale = ['rgba(0, 0, 255, 0)', 
                                          'rgba(0, 255, 0, 0.05)', 
                                           'rgba(0, 255, 0, 0.1)'],
                            reversescale=False,
                            showscale=False,
                            opacity=1,
                            )
            )


    
    if 'dub29' in gachecklist:
# green markers for ga of lsmd --------
        for _, group in df_ga_lsmd.query(
            "(284 < HeadingTrue < 290) & (RocRod > 1)"
        ).groupby("ID"):
            if len(group) > 0:
                fig.add_traces(
                    go.Scatter(
                        mode="markers",
                        x=-np.sign((group["SwissGridX"] - ga_lsmd.rwy_sgx))
                        * np.sqrt(
                            (group["SwissGridX"] - ga_lsmd.rwy_sgx) ** 2
                            + (group["SwissGridY"] - ga_lsmd.rwy_sgy) ** 2
                        ),
                        y=group["AltitudeBaro"] / 0.3048,
                        marker=dict(size=6, color="green", symbol="square-open"),
                        showlegend=False,
                        name='Dueb. GA marker',
                    )
                )

    fig.update_layout(
        yaxis_range=[2000, 7800],
        xaxis_range=[-7750, 12750],
        margin={"r": 20, "t": 20, "l": 20, "b": 20},
    )

    fig.update_yaxes(gridcolor="black")
    fig.update_xaxes(gridcolor="black")
    fig.update_layout(height=600)

    # add existing GAs here
    return fig


@app.callback(
    Output('ga-trajs',"figure"),
    [
     Input('traj-checklist','value')
     ])
def plot_dub_lszh_goarounds(trajchecklist):

        fig_lszh = go.Figure()
        
        if 'lines' in trajchecklist:
            fig_lszh = px.line_mapbox(
                df_ga_lszh14_spatfilt, lat="Lat", lon="Lon", line_group="ID"
            )
            fig_lszh.update_traces(line=dict(color="darkblue", width=0.5))
            fig_lszh.update_layout(mapbox_style="carto-positron")


        if 'dens' in trajchecklist:
            fig_lszh = px.density_mapbox(
                df_ga_lszh14_spatfilt,
                lat="Lat",
                lon="Lon",
                radius=5,
                center=dict(lat=47.35, lon=8.66),
                zoom=11,
                color_continuous_scale="Hot_r",
                range_color=[0, 10],
                mapbox_style="carto-positron",
            )
            fig_lszh.update_layout(coloraxis_showscale=False)


        fig_lsmd = px.line_mapbox(df_ga_lsmd, lat="Lat", lon="Lon", line_group="ID")
        fig_lsmd.update_layout(mapbox_style="carto-positron")
        fig_lsmd.update_traces(line=dict(color="black", width=0.5))
        for traces in fig_lsmd.data:
            fig_lszh.add_traces(traces)
        fig = fig_lszh

        zoom, center = dashboard.zoom_center(
            tuple(df_ga_lszh14_spatfilt["Lon"]) + tuple(df_ga_lsmd["Lon"]),
            tuple(df_ga_lszh14_spatfilt["Lat"]) + tuple(df_ga_lsmd["Lat"]),
        )
        center["lon"] += 0.05
        center["lat"] -= 0.05
        fig.update_layout(mapbox=dict(center=center, zoom=zoom - 0.5))

        fig.update_layout(
            margin={"r": 20, "t": 20, "l": 20, "b": 20},
        )
        
        
        return fig
    






# save the collision risk below sliders if there is simultaneous GA in lszh and lsmd to store object
@app.callback(
    Output("probability-simlt-ga-data", "data"),
    [
        Input("altini-slider", "value"),
        Input("altlvl-slider", "value"),
        Input("gspcli-slider", "value"),
        Input("roccli-slider", "value"),
    ],
)
def calculate_simlt_colprob(altini, altlvl, gspcli, roccli):
    gsplvl = 200  # Does not have impact on proba col

    ga_lsmd = GaTrajGen(
        airport="LSMD",
        runway=29,
        glideslope=4.5,
        boundaries=[
            min(sgx_bounds),
            min(sgy_bounds),
            max(sgx_bounds),
            max(sgy_bounds),
        ],
    )

    # generate a few example trajectories
    ga_traj = ga_lsmd.generate_ga(
        alt_ini=altini,
        alt_lvl=altlvl,
        gsp_cli=gspcli,
        gsp_lvl=gsplvl,
        roc_cli=roccli,
        dt=1,
    )
    pcol_simlt_ga = dashboard.proba_col_when_simult_landings(
        ga_traj, kde_dict, theta=120, vga_lszh=115, dt=1
    )

    # return "{:.2e}".format(pcol_simlt_ga)
    return pcol_simlt_ga


# route the stored value to the html.P display container
@app.callback(
    Output("probability-simlt-ga", "children"),
    [
        Input("probability-simlt-ga-data", "data"),
    ],
)
def output_simlt_ga_probability(value):
    return "{:.2e} x Prob. of having simultaneous GAs".format(value)


# calculate the probabilty of collision with method 1


@app.callback(
    Output("prob-result-method1", "children"),
    Output("prob-result-sim_ga", "children"),
    [
        Input("probability-simlt-ga-data", "data"),
        # Input("altini-slider", "value"),
        # Input("altlvl-slider", "value"),
        # Input("gspcli-slider", "value"),
        # Input("roccli-slider", "value"),
        Input("rategadub-inpt", "value"),
        Input("pagazwhengadub-inpt", "value"),
        # Input("plndzwhenlndd-inpt", "value"),
    ],
)
def calculate_collision_probability_method1(
    pcol_simlt_ga,
    # altini,
    # altlvl,
    # gspcli,
    # roccli,
    rategadubinpt,
    pagazwhengadubinpt,
    # plndzwhenlnddinpt,
):
    # gsplvl = 200  # Does not have impact on proba col

    # ga_lsmd = GaTrajGen(
    #     airport="LSMD",
    #     runway=29,
    #     glideslope=4.5,
    #     boundaries=[
    #         min(sgx_bounds),
    #         min(sgy_bounds),
    #         max(sgx_bounds),
    #         max(sgy_bounds),
    #     ],
    # )

    # # generate a few example trajectories
    # ga_traj = ga_lsmd.generate_ga(
    #     alt_ini=altini,
    #     alt_lvl=altlvl,
    #     gsp_cli=gspcli,
    #     gsp_lvl=gsplvl,
    #     roc_cli=roccli,
    #     dt=1,
    # )
    # pcol_simlt_ga = dashboard.proba_col_when_simult_landings(
    #     ga_traj, kde_dict, theta=120, vga_lszh=115, dt=1
    # )
    p_sim_ga = pagazwhengadubinpt * rategadubinpt / 1000
    pcol_when_lnd_dub_rel = (
        pcol_simlt_ga * p_sim_ga  # same as p_ga_dub_and_ga14_dep
    )
    # return str(pcol_when_lnd_dub_rel)
    return "{:.2e}".format(pcol_when_lnd_dub_rel), "{:.2e}".format(p_sim_ga)


# calculate the probabilty of collision with method 2


@app.callback(
    [
        Output("prob-result-method2", "children"),
        Output("p_ga_dub_and_ga14_dep", "children"),
    ],
    [
        Input("probability-simlt-ga-data", "data"),
        # Input("altini-slider", "value"),
        # Input("altlvl-slider", "value"),
        # Input("gspcli-slider", "value"),
        # Input("roccli-slider", "value"),
        Input("rategadub-2-inpt", "value"),
        Input("rategazue14-inpt", "value"),
        Input("rho-inpt", "value"),
        Input("plndzwhenlnddue-inpt", "value"),
    ],
)
def calculate_collision_probability_method2(
    pcol_simlt_ga,
    # altini,
    # altlvl,
    # gspcli,
    # roccli,
    rate_ga_dub,
    rate_ga_14,
    rho,
    p_lnd14_when_lnd29,
):

    gsplvl = 200  # Does not have impact on proba col

    rate_ga_dub = rate_ga_dub / 1000
    rate_ga_14 = rate_ga_14 / 1000

    var_ga_dub = rate_ga_dub * (1 - rate_ga_dub)
    var_ga_14 = rate_ga_14 * (1 - rate_ga_14)
    p_ga_dub_and_ga14_dep = (
        rho * np.sqrt((var_ga_dub * var_ga_14)) + rate_ga_dub * rate_ga_14
    )
    p_ga_dub_and_ga14_dep *= p_lnd14_when_lnd29

    # ga_lsmd = GaTrajGen(
    #     airport="LSMD",
    #     runway=29,
    #     glideslope=4.5,
    #     boundaries=[
    #         min(sgx_bounds),
    #         min(sgy_bounds),
    #         max(sgx_bounds),
    #         max(sgy_bounds),
    #     ],
    # )

    # # generate a few example trajectories
    # ga_traj = ga_lsmd.generate_ga(
    #     alt_ini=altini,
    #     alt_lvl=altlvl,
    #     gsp_cli=gspcli,
    #     gsp_lvl=gsplvl,
    #     roc_cli=roccli,
    #     dt=1,
    # )

    # pcol_simlt_ga = dashboard.proba_col_when_simult_landings(
    #     ga_traj, kde_dict, theta=120, vga_lszh=115, dt=1
    # )
    pcol_when_lnd_dub = pcol_simlt_ga * p_ga_dub_and_ga14_dep

    return "{:.2e}".format(pcol_when_lnd_dub), "{:.3g}".format(
        p_ga_dub_and_ga14_dep
    )  # str(p_ga_dub_and_ga14_dep)


# --- run the server
if __name__ == "__main__":
    # host = "160.85.67.62"
    # app.run_server(debug=True, host=host, port=8055)
    app.run_server(debug=True, use_reloader=False)
