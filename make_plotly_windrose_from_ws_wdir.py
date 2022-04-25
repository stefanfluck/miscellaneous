import plotly.express as px
import pandas as pd

import plotly.io as pio
pio.renderers.default = "svg"
#%%

df = pd.read_csv('Desktop/neuhegi_ostluft.csv', sep=';')
df.columns = ['start','end','wdir','ws']


bins_mag= [-0.01, 1, 2, 3, 4, 5, 6,15]
bins_mag_labels = ['0-1','1-2','2-3','3-4','4-5', '5-6',' 6+']

bins_dir = [-0.01, 11.25, 33.75, 56.25, 78.75,101.25,123.75,146.25,168.75,191.25,213.75,236.25,258.75,281.25,303.75,326.25,348.75, 360.00]
bins_dir_labels = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW','North']

df['mag_binned'] = pd.cut(df['ws'], bins_mag, labels=bins_mag_labels)
df['dir_binned'] = pd.cut(df['wdir'],bins_dir, labels=bins_dir_labels)

dfe = df[['mag_binned', 'dir_binned']].copy() #here i am creating a new dataframe, with necessary columns only (except the last one, which I will convert to frequencies column
dfe['freq'] = 0

g = dfe.groupby(['mag_binned','dir_binned']).count() #grouping
g.reset_index(inplace=True) 
g['percentage'] = g['freq']/g['freq'].sum()
g['percentage%'] = g['percentage']*100
g['Magnitude [m/s]'] = g['mag_binned']
g = g.replace(r'North', 'N', regex=True) #replacing remaining Norths with N 






fig = px.bar_polar(g, r="percentage%", theta="dir_binned",
                   color="Magnitude [m/s]",
                   color_discrete_sequence= px.colors.sequential.Brwnyl)
#fig.update_polars(bgcolor='rgba(0,0,0,0)')
fig.update_layout(template=None,
    title_x=0.5,
    font_size=8,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend_font_size=10,
    legend_x=1.1,
    legend_y=0.89,
    legend_xanchor='right',
    polar_radialaxis_ticksuffix='%',
    polar = dict( radialaxis_angle = 180,
        radialaxis = dict(showgrid= True, showline= True, tickfont_color="Black", linecolor='rgba(70,70,70,0.5)', gridcolor="gray", tickangle = 180 , ticks="outside", showticklabels=True),
        angularaxis = dict(visible=False, showline=True, showgrid= False, linecolor="Gray", showticklabels=False, ticks ="")
    ),
    polar_angularaxis_rotation=90,
   
    font=dict(
        family="Arial",
        size=8,
        color="black")
)

fig.show()

