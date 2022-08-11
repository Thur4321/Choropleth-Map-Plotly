import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd 
import plotly.express as px
import json
from collections import OrderedDict
import urllib
with urllib.request.urlopen('https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-35-mun.json') as response:
    geo = json.load(response)
    
app = dash.Dash(__name__)

dfcities = pd.read_csv('BRAZIL_CITIES_REV2022.csv', usecols = ['CITY', 'STATE', 'LONG', 'LAT'])

dfmask = dfcities['STATE'] == 'SP'

dfsp = dfcities[dfmask]

dfsp.rename(columns={'CITY': 'Munic', 'LAT':'lon', 'LONG':'lat'}, inplace = True)
colnames = ['Munic','code','uf','nome_est','lat','lon','data','preci','nan']
df=pd.read_csv("data.csv", sep=';', names=colnames) 
df = df.iloc[1: , :].reset_index(drop=True)
df = df.replace({',':'.'}, regex = True)
del df['nan']
df['data'], df['hora'] = df['data'].str.split(' ', 1).str
df['data'] = df['data'].astype(str, errors = 'raise')
df['preci'] = df['preci'].astype(float, errors = 'raise')
df['Munic'] = df['Munic'].str.capitalize()
df = df.groupby(['Munic', 'code', 'uf', 'nome_est', 'lat', 'data']).agg({'preci':'sum'}).reset_index()
datalist = list(OrderedDict.fromkeys(df['data'].tolist()))

app.layout = html.Div([
    html.H1('Web Application Dashboards with Dash', style = {'text-align':'center'}),
    dcc.Dropdown(id = 'slct_day',
                options = datalist,
                multi = False,
                value = '2022-02-01',
                style = {'width':'40%'}
                ),
    html.Div(id = 'output_container', children = []),
    html.Br(),
    dcc.Graph(id = 'Rain_Map', figure = {})
    
])

@app.callback(
    [Output(component_id = 'output_container', component_property = 'children'),
     Output(component_id = 'Rain_Map', component_property = 'figure')],
    [Input(component_id = 'slct_day', component_property = 'value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))
     
    container = 'O dia escolhido pelo usuário é: {}'.format(option_slctd)
     
    dff = df.copy()
    dff = dff[dff['data'] == option_slctd]
    dff = pd.concat([dff, dfsp]).sort_values(by = 'Munic')
    dff.interpolate('nearest', columns = 'preci', inplace = True)
     
    fig = px.choropleth_mapbox(dff,
                           geojson = geo,
                           locations="Munic",
                           featureidkey = 'properties.name',
                           color = "preci",
                           color_continuous_scale="Spectral",
                           mapbox_style = "carto-positron", #defining a new map style
                           center = {"lat":-22.77972, "lon": -48.5},
                           zoom = 5,
                           opacity = 0.9
    )
    return container, fig

if __name__ == '__main__':
    app.run_server(port = 3003, debug=True)