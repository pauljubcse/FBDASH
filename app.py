import dash
from dash import dcc
from dash import html 
import plotly.graph_objs as go
import numpy as np
from dash.dependencies import Input, Output, State
import yfinance as yf
import dash_auth
from datetime import datetime
import pandas as pd
import requests
import pandas as pd
from bs4 import BeautifulSoup
import seaborn as sb
import warnings
import numpy as np
from math import pi
from googlesearch import search
import time
app = dash.Dash()
AUTH=[['fbref', 'fbref']]
auth =dash_auth.BasicAuth(app, AUTH)
server=app.server

names=pd.read_csv('NAME_DB.csv')
names=names.drop(['Unnamed: 0'], axis=1)
names.set_index('Name', inplace=True)
options=[]
#print(names.head(5))
for name in names.index:
    try:
        options.append({'label': name, 'value':name })
    except:
        continue
#print(options)
app.layout = html.Div([
    #html.Div('Dash: Web Dashboards with Python', style={'textAlign':'center', 'color':colors['text']}),
    html.Div([
        html.H1('FBRef Player Comparison Dashboard with Python', style={'textAlign':'center', 'color':'#9BA4B5','font-family' : "'Roboto', sans-serif"}),
        html.P(),
        html.Div([
            html.Div([
                html.H3('Enter Player Name', style={
                                                    'textAlign':'center',
                                                    'color':'#9BA4B5',
                                                    'font-family' : "'Roboto', sans-serif"
                                                    }),
                html.P(),
                dcc.Dropdown(
                    id='name-select',
                    options=options,
                    value=['Harry Kane'],
                    multi=True
                )
            ], style={
                
            }),
            
        ]),

        html.Div([
            html.Div([
                html.Button(id='submit-button', n_clicks=0, children='Submit',
                        style={
                            'font-family' : "'Roboto', sans-serif",
                            'width':'120px',
                            'height':'50px',
                            'border-radius':'10px',
                        })
            ], style={'paddingTop':'55px'})

        ], style = {
            'display' :'flex',
            'flex-direction' : 'row',
            'justify-content' : 'space-around'
        }),
        
        
        html.P(),
        dcc.Graph(id='player-graph', figure={'data':[go.Scatter(x=[1,2,3], y=[1,2,3], mode='lines' )],
                                            'layout': go.Layout(title='TITLE',template='plotly_dark')}),

        
    ], id='main',
    style={
        'background-color':'#000000',
        'padding':'25px',
        'border-radius' : '5px',
        'box-shadow' : '0 0 150px 30px #000000',
        'display':'flex',
        'flex-direction':'column'
        },
    )
])

def linkGen(player):
    query = player+" FBref"
    print(query)
    for j in search(query):
        #print(j)
        return j

def getPlayerData(x):
    warnings.filterwarnings("ignore")
    print(x)
    try:
        url = x
        page =requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        div=soup.find("div", {"class" : "filter switcher"})
        pos=div.find("a").contents[0][4:]

        name = [element.text for element in soup.find_all("span")]
        name = name[7]
        metric_names = []
        metric_values = []
        metric_percentiles = []
        remove_content = ["'", "[", "]", ","]
        for row in soup.findAll('table')[0].tbody.findAll('tr'):
            first_column = row.findAll('th')[0].contents
            if first_column==[]:
                continue
            metric_names.append(first_column[0])
        for row in soup.findAll('table')[0].tbody.findAll('tr'):
            first_column = row.findAll('td')[0].contents
            if first_column==[]:
                continue
            metric_values.append(first_column[0])
        for row in soup.findAll('table')[0].tbody.findAll('tr'):
            first_column = row.findAll('td')[1].contents
            if first_column==[]:
                continue
            metric_percentiles.append(int(first_column[0].contents[0]))
        for i in range(len(metric_values)):
            text=metric_values[i]
            if '%' in text:
                text=text[:-1]
            metric_values[i]=float(text)
        #print([metric_names, metric_values, metric_percentiles, name, pos])
        return [metric_names, metric_values, metric_percentiles, name, pos]
    except:
        #print("L")
        return []
    
@app.callback(
        Output('player-graph','figure'),
        [Input('submit-button', 'n_clicks')],
        [State('name-select','value')]
    )
def update_graph(n_clicks, players):
    print("-------------------------------------------")
    alldata=[]
    refined=[]
    
    print(players)
    for player in players:
        try:
            print(player)
            temp=getPlayerData(linkGen(player))
            if(temp!=[]):
                alldata.append(temp)
            refined.append(player)
            print("Player: ", player, " Found")
        except:
            print("Player: ", player, " Data doesn't exist.")
    if len(refined)==0:
        return

    categories = [str(i) for i in alldata[0][0]]

    data=[]
    for data_i in alldata:
        data.append(go.Scatterpolar(r=data_i[2], theta=categories, fill='toself', name=data_i[3]))
    
    fig = go.Figure(
        data=data,
        layout=go.Layout(
            autosize=True,
            title=go.layout.Title(text='Player Comparison'),
            polar={'radialaxis': {'visible': True}},
            template='plotly_dark',
            showlegend=True
        )
    )
    return fig

if __name__=='__main__':
    app.run_server()