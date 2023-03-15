import pandas as pd
import plotly.express as px
from pandas_datareader import wb

from dash import dcc, html, Dash
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

dbc_css = 'https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css'

# Template for figures
load_figure_template('bootstrap')

# First get countries info from wb

# Import country info
df_info = wb.get_countries()

# Drop aggregates, i.e., keep only countries
df_info = df_info[df_info['region'] != 'Aggregates'].copy()
df_info.rename(columns = {'name' : 'country'}, inplace = True)

# Define dict with indicators
ind_dict = {'FP.CPI.TOTL.ZG' : 'CPI'}

# Import data on indicators
df_wb = wb.download(indicator = ind_dict.keys(), country = 'all', start = 2000, end = 2023).reset_index()

# Rename and change dtype
df_wb.rename(columns = ind_dict, inplace = True)
df_wb['year'] = df_wb['year'].astype(int)

# Inner join with country info (to keep only countries)
df_wb = df_wb.merge(df_info, on = 'country', how = 'inner')


# Create options for which countries we want to choose
options = []
for country in df_wb['country'].unique():
    options.append({'label' : country, 'value' : country})

# Save countries for dropdown menu later
countries = dcc.Dropdown(
    id = 'my_input',
    options = options,
    value = 'Norway',
    multi = True
)

# Application
app = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP, dbc_css])
server = app.server

app.layout = dbc.Container(
    children = [

        # Header
        html.H1('Inflation around the world'),
        html.P('Comparison between chosen countries'),

        # Input component - dropdown menu
        html.Label('Select countries:'),
        countries,

        # Output component - graph
        dcc.Graph(id = 'my_output')

    ],
    className = 'dbc'
)

@app.callback(
    Output('my_output', 'figure'),
    Input('my_input', 'value')
)

def wb_line(country_lst, df=df_wb):
    # Convert country_lst to a list if it is a string
    if not isinstance(country_lst, list):
        country_lst = [country_lst]

    # Copy df and filter by selected countries
    df_copy = df[df['country'].isin(country_lst)].copy()

    # Sort data according to year
    df_copy.sort_values(['year'], inplace=True)

    # Add column with empty string
    df_copy['label'] = ''

    # Swap empty string with country names
    for country in country_lst:
        df_copy.loc[df_copy['country'] == country, 'label'] = country

    # Create scatter plot
    fig = px.line(
        df_copy,
        x='year',
        y='CPI',
        color='country',
        hover_name='country',
    )

    # Update y-axis range based on selected countries' inflation values
    fig.update_yaxes(range=[df_copy['CPI'].min(), df_copy['CPI'].max()])

    fig.update_traces(textposition='top center')

    fig.update_layout(
        yaxis_title='Inflation in %',
        xaxis_title='Year',
        showlegend=True,
    )


    return fig



app.run_server()