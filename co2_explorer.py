import pandas as pd
import plotly.express as px
from pandas_datareader import wb

from dash import dcc, html, Dash
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

dbc_css = 'https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css'
load_figure_template('bootstrap')

# Import the data
df = pd.read_csv('world_1960_2021.csv')

# Change year column type
df['year'] = pd.to_datetime(df['year'], format = '%Y')

# Change column names and to upper
df.columns = ['COUNTRY', 'YEAR', 'TOTAL_CO2', 'CO2_PER_CAPITA']

# Drop NA
df.dropna(inplace = True)


# Copy df
df_copy = df.copy()

# Sort data according to year
df_copy.sort_values(['YEAR'], inplace = True)

# Create line plot
fig = px.line(
    df_copy,
    x = 'YEAR',
    y = 'TOTAL_CO2'
)

fig.update_layout(
    yaxis=dict(title='Total CO2'),
    yaxis2=dict(title='CO2 Per Capita', overlaying='y', side='right',
                tickfont=dict(color='red')),
    xaxis_title = 'CO2 Around the world',
    showlegend = False
)

fig.add_scatter(x=df['YEAR'],
                y=df['CO2_PER_CAPITA'],
                mode='lines',
                yaxis = 'y2',
                hovertext=df['CO2_PER_CAPITA'])

fig.update_traces(textposition='top center')


app = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP, dbc_css])
server = app.server

app.layout = dbc.Container(
    children = [
        
        # Header
        html.H1('CO2 emissions around the world'),
        dcc.Markdown(
            """Data on emissions and potential drivers are extracted from the 
               [World Development Indicators](https://datatopics.worldbank.org/world-development-indicators/) 
               database."""
        ),
        dcc.Graph(figure = fig)
        
    ],
    className = 'dbc'


)
app.run_server()