import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd 
import numpy as np
import datetime 
import time
import warnings
import os
import plotly.express as px
import plotly.graph_objs as go
import dash_daq as daq


warnings.filterwarnings("ignore")

###################################################################
# Define all Constants and Look up area here                      #
###################################################################

menu_dict_list=[]
menu_values=[]
labels = ['Confirmed','Recovered','Deaths'] 
#external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

colors = {
    'background': '#1e1e1e',
    'plotbackground': '#000000',
    'borderline' : '#ffffff',
    'backgroundrecovered': '#000000',
    'backgroundconfirmed': '#000000',
    'textrateofraise' :'#ff7518',
    'textrecovered': '#138808',
    'textconfirmed': '#1e948a',
    'textdeaths': '#B20000',
    'amber': '#FFA500',
    'text': '#ff7518',
    'mapmarkers':'#B20000',
    'ledtext' : '#ff7518',
    'ledbackground':'#1f1f1f',
    'pie_colors' : ['#6a5acd','#018d61','#d40000']
}

MAPBOX_ACCESS_TOKEN = "pk.eyJ1Ijoic2FudG9zaGNiaXQyMDAyIiwiYSI6ImNrODhrM2V3djA4djAzcXFhanh2eHpiM20ifQ.X9kcJYiDV41QidY4DgYVcA"
MAPBOX_STYLE="mapbox://styles/santoshcbit2002/ck88qasdh2dpe1ip5io9mauu9"

data_refreshed_text='Data Source : John Hopkins University, USA. Data refreshed on this page : ' + str(datetime.datetime.now().date())

###################################################################
# Load data into dataframe.                                       #
################################################################### 
print('*'*50)
print('Program has started  - {}'.format(datetime.datetime.now()))
print('Current Working Directory: {}'.format(os.getcwd()))
print('Loading Datasets : ')
# Plots 1,2,3 and 5
confirmed_cases_frame=pd.read_csv('pre_processed_confirmed_cases.csv')
recovered_cases_frame=pd.read_csv('pre_processed_recovered_cases.csv')
deaths_cases_frame=pd.read_csv('pre_processed_deaths_cases.csv')
# Plots 4
confirmed_max_date=pd.read_csv('pre_processed_confirmed_max_date.csv')
recovered_max_date=pd.read_csv('pre_processed_recovered_max_date.csv')
deaths_max_date=pd.read_csv('pre_processed_deaths_max_date.csv')
# Plot 6
confirmed_cases_timeline=pd.read_csv('pre_processed_confirmed_cases_timeline.csv')

print('pre_processed_confirmed_cases - data read complete. Shape of data {}'.format(confirmed_cases_frame.shape))
print('pre_processed_recovered_cases - data read complete. Shape of data {}'.format(recovered_cases_frame.shape))
print('pre_processed_deaths_cases - data read complete. Shape of data {}'.format(deaths_cases_frame.shape))
print('pre_processed_confirmed_max_date - data read complete. Shape of data {}'.format(confirmed_max_date.shape))
print('pre_processed_recovered_max_date - data read complete. Shape of data {}'.format(recovered_max_date.shape))
print('pre_processed_deaths_max_date - data read complete. Shape of data {}'.format(deaths_max_date.shape))
print('pre_processed_confirmed_cases_timeline - data read complete. Shape of data {}'.format(confirmed_cases_timeline.shape))


print('-'*50)

###################################################################
# Prepare Data for Drop Down Menu                                 #
################################################################### 

countries=list(confirmed_cases_frame['Country'].unique())

for i in countries:
    menu_dict={}
    menu_dict['label']=i
    menu_dict['value']=i
    menu_values.append(i)
    menu_dict_list.append(menu_dict)

###################################################################
# Prepare Data for Time Line Graph                                #
################################################################### 

# No preparation needed for the data. 

###################################################################
# Prepare Data for Rate of raise graph                             #
################################################################### 
 
temp=confirmed_cases_frame[confirmed_cases_frame['Country']=='China'][['Dates','Confirmed']]
temp['Dates']=pd.to_datetime(temp['Dates'],format='%Y-%m-%d')
temp=temp.set_index('Dates')
temp=temp.diff()
temp.dropna(inplace=True)
rate_of_increase_sampled=temp.resample('D').interpolate()[::7]


###################################################################
# Prepare Data for Pie Graph                                      #
################################################################### 

deaths=deaths_max_date[deaths_max_date['Country'].isin(['China'])]['Deaths'].sum()
recovered=recovered_max_date[recovered_max_date['Country'].isin(['China'])]['Recovered'].sum()
confirmed=confirmed_max_date[confirmed_max_date['Country'].isin(['China'])]['Confirmed'].sum()
   
labels=['Confirmed','Recovered','Deaths']
values=[confirmed,recovered,deaths]

###################################################################
# Prepare Data for World Statistic                                #
################################################################### 

confirmed_cases=confirmed_max_date['Confirmed'].sum()
recovered_cases=recovered_max_date['Recovered'].sum()
deaths_cases=deaths_max_date['Deaths'].sum()


confirmed_count = html.Div(
    id="confirmed-count",
    children=[
        daq.LEDDisplay(
            id="confirmed-count-led",
            value=confirmed_cases,
            label={'label':"Confirmed cases in the world",
            'style': {
                'font-size':'130%',
                'font-family':'Open Sans', 
                'font-weight': 'normal',
                'color': colors['text'],
                'border-color':colors['background']
                    }
                    },
            size=21,
            color=colors['amber'],
            style={"color": '#black'},
            backgroundColor=colors['ledbackground']
        )
    ]
)

recovered_count = html.Div(
    id="recovered-count",
    children=[
        daq.LEDDisplay(
            id="recovered-count-led",
            value=recovered_cases,
            label={'label':"Recovered cases in the world",
            'style': {
                'font-size': '130%',
                'font-family':'Open Sans', 
                'font-weight': 'normal',
                'color': colors['text'],
                'border-color':colors['background']
            }},
            size=22,
            color=colors['amber'],
            style={"color": '#black'},
            backgroundColor=colors['ledbackground']
        )
    ]
)

deaths_count = html.Div(
    id="deaths-count",
    children=[
        daq.LEDDisplay(
            id="deaths-count-led",
            value=deaths_cases,
            label={'label':"Deaths in the world",
            'style': {
                'font-size': '130%',
                'font-family':'Open Sans',
                'font-weight': 'normal', 
                'color': colors['text'],
                'letter-spacing': 1.0,
                'border-color':colors['plotbackground']
            }},
            size=23,
            color=colors['amber'],
            style={"color": '#black','margin':0},
            backgroundColor=colors['ledbackground']
        )
    ],style={'border-color':colors['plotbackground']}
)

###################################################################
# Prepare Data for Map                                            #
################################################################### 

# Get data for Map
id=0

max_interval_count=len(confirmed_cases_timeline)
map_text=confirmed_cases_timeline[confirmed_cases_timeline['Date_id']==id]['Country']
latitude=confirmed_cases_timeline[confirmed_cases_timeline['Date_id']==id]['latitude']
longitudes=confirmed_cases_timeline[confirmed_cases_timeline['Date_id']==id]['longitudes']

# Create Map Data 
map_data = [
      {
        "type": "scattermapbox",
        "lat": [0.1],
        "lon": [0.1],
        "hoverinfo": "text",
        "text": "text",  
        "mode": "lines",
        "line": {"color": colors['plotbackground']},
    },
    {
        "type": "scattermapbox",
        "lat": latitude,
        "lon": longitudes,
        "hoverinfo": "text+lon+lat",
        "text": map_text,
        "mode": "scattermapbox",
        "marker": {"size": 10, "color": colors['mapmarkers']}
    },
]

map_layout = {
    "mapbox": {
        "accesstoken": MAPBOX_ACCESS_TOKEN,
        "style": MAPBOX_STYLE,
         "center": [60.5000209,9.0999715],
         "zoom": 0.9
    },
    "showlegend": False,
    "autosize": True,
    "paper_bgcolor": colors['plotbackground'],
    "plot_bgcolor": colors['plotbackground'],
    "margin": {"t": 0, "r": 20, "b": 0, "l": 0},
}

map_graph = html.Div(
  #  id="world-map-wrapper",
    children=[
        dcc.Graph(
            id="world-map",
            figure={"data": map_data, "layout": map_layout},
            config={"displayModeBar": False, "scrollZoom": True},
        ),
    ],
)

##############################################################################
#                               Create DASH App instance                     #
##############################################################################

#app = dash.Dash(external_stylesheets=external_stylesheets)
app = dash.Dash()

##############################################################################
#                               HTML Layout                                  #
##############################################################################

app.layout = html.Div(
    style={'backgroundColor': colors['plotbackground']},
children=[
    html.H2(
        style={
        'textAlign': 'center', 
        'backgroundColor':colors['plotbackground'],
        'padding': '12px',
        'color': colors['text'],
        'font-size':'300%',
        'font-family':'Open Sans', 
        'font-weight': 'normal',
        'letter-spacing': 1.0,
        'margin': 0},
        children='COVID - 19 Dashboard'

            ),

    html.Div( style={'backgroundColor': colors['plotbackground']},
            children=[
            html.H3(
                    children=data_refreshed_text,
                     style={
                        'textAlign': 'center', 
                        'backgroundColor':colors['plotbackground'],
                        'color': colors['text'],
                        'font-size':'100%',
                        'font-family':'Open Sans', 
                        'font-weight': 'normal',
                        'letter-spacing': 0.2
                        },
                    )   
            ]),
    
    html.Div(
        [ html.Div([
            html.Label( 
                [
                "Select upto five countries",
                dcc.Dropdown(
                id='countries-menu',
                options=menu_dict_list,
                value=['China','US','United Kingdom','Spain','Italy'],
                placeholder="Select Countries",
                multi=True
                        ),
                    ])
             ])],
        style={'width': '20%', 
                'backgroundColor': colors['plotbackground'],
                'margin': '15px',
                 'color': colors['text'],
                'font-size':'100%',
                'font-family':'Open Sans', 
                'font-weight': 'normal',
                 }
                    ),   
    html.Div(
           style={'backgroundColor': colors['plotbackground'],'columnCount':2},
           children=[
                    html.Div([   
                    dcc.Graph(
                        id='ratio_of_cases',
                        figure={
                            'data':  [
                                    go.Pie(labels=labels,
                                        values=values,hole=0.5)
                                       ],  
                            'layout':{
                                    'title':'Proportion of recovery, deaths and confirmed cases',
                                    'plot_bgcolor': colors['background'],
                                        'paper_bgcolor': colors['background'],
                                        'font': {'color': colors['textrateofraise']},
                                         "margin": {"t": 0, "r": 20, "b": 0, "l": 0},
                                        'style': {  'width': '60%',
                                                    'height': '40px',
                                                    'lineHeight': '60px',
                                                    'borderWidth': '5px',
                                                    'borderStyle': 'dashed',
                                                    'borderRadius': '5px',
                                                    'textAlign': 'center'
                                                
                                               }     
                                        }  
                                }   
                            )   
                    ],
                style={'width': '80%','backgroundColor': colors['plotbackground'],
                'margin-left': '40px'}
                ),

                html.Div([
                    dcc.Interval(id="interval", interval=1 * 1000, n_intervals=0,max_intervals=max_interval_count),
                    html.Div([
                        html.Label([
                        "Animation of spread of infections across globe",
                        dcc.Graph(id="world-map",
                        figure={
                            'data': map_data, 
                            'layout': map_layout
                                },
                        config={'displayModeBar': False, 
                                'scrollZoom': True},
                                ),
                                ])
                        ],style={'backgroundColor': colors['plotbackground'],'font': {'color': colors['textrateofraise']},}
                 ) ]),
           ]),
    
    html.Div(
        id="led-displays",
        children=[confirmed_count, recovered_count,deaths_count],
            style={'columnCount':3,'border-color':colors['plotbackground']}
                    ),

    html.Div( 
        style={'backgroundColor': colors['plotbackground'],'columnCount':2},
        children=[
           html.Div([
                    dcc.Graph(
                        id='timeline_deaths',
                        figure={
                                'data': [
                                    go.Scatter(x=deaths_cases_frame[deaths_cases_frame['Country']=='China']['Dates'],
                                                y=deaths_cases_frame[deaths_cases_frame['Country']=='China']['Deaths'],
                                                name='China',
                                                mode='lines')
                                       ],
                                'layout': {
                                    'title':{ 'text':'Time line of deaths'},
                                    'plot_bgcolor': colors['plotbackground'],
                                    'paper_bgcolor': colors['plotbackground'],
                                    'font': {'color': colors['textdeaths']},
                                    'margin': '0',
                                        'padding': '20px',   
                                        'style': {  'width': '100%',
                                                    'height': '40px',
                                                    'border': '5px solid orange',
                                                    'borderWidth': '5px',
                                                    'borderStyle': 'solid',
                                                    'borderRadius': '5px',
                                                    'textAlign': 'center' 
                                               }           
                                       }
                                }
                            )  
                    ],
                 style={
                'backgroundColor': colors['plotbackground'] }
                ),
         html.Div([   
                   dcc.Graph(
                        id='timeline_recovered_cases',
                        figure={
                                'data': [
                                    go.Scatter(x=recovered_cases_frame[recovered_cases_frame['Country']=='China']['Dates'] ,
                                    y=recovered_cases_frame[recovered_cases_frame['Country']=='China']['Recovered'],
                                                name='China',
                                                mode='lines')
                                       ],
                                'layout': {
                                    'title':{ 'text':'Time line of recovered cases'},
                                    'plot_bgcolor': colors['plotbackground'],
                                    'paper_bgcolor': colors['plotbackground'],
                                    'font': {'color': colors['textdeaths']},
                                    'margin': '0',
                                        'padding': '20px',   
                                        'style': {  'width': '100%',
                                                    'height': '40px',
                                                    'border': '5px solid orange',
                                                    'borderWidth': '5px',
                                                    'borderStyle': 'solid',
                                                    'borderRadius': '5px',
                                                    'textAlign': 'center' 
                                               }           
                                       }
                                }
                            )  
                        ],
                       style={'width': '100%','backgroundColor': colors['plotbackground']}
            )
            ]),

    html.Div(
        style={'backgroundColor': colors['plotbackground'],'columnCount':2},
        children=[
                 html.Div([   
                    dcc.Graph(
                        id='rate_of_spread_plot',
                        figure={
                                'data': [
                                    go.Scatter(x=rate_of_increase_sampled.index,
                                                y=rate_of_increase_sampled['Confirmed'], 
                                                line={'color':colors['mapmarkers'], 'width':4},  
                                                marker={'size':10})
                                ],
                                'layout':{
                                    'title':{ 'text':'Rate of increase in confirmed cases'},
                                    'plot_bgcolor': colors['plotbackground'],
                                        'paper_bgcolor': colors['plotbackground'],
                                        'font': {'color': colors['textrateofraise']},
                                        'yaxis': { 'gridcolor': "#636363", "showline": False},
                                        'xaxis': { 'gridcolor': "#636363", "showline": False},
                                        'style': {  'width': '100%',
                                                    'height': '60px',
                                                    'lineHeight': '60px',
                                                    'borderWidth': '5px',
                                                    'borderStyle': 'dashed',
                                                    'borderRadius': '5px',
                                                    'textAlign': 'center',
                                                    'margin': '10px'
                                                
                                               }           
                                       }
                                }
                            )  
                    ],
                style={'width': '100%','backgroundColor': colors['background']}
                ),
 html.Div([   
                    dcc.Graph(
                        id='timeline_confirmed_cases',
                        figure={
                                'data': [
                                    go.Scatter(x=confirmed_cases_frame[confirmed_cases_frame['Country']=='China']['Dates'],
                                            y=confirmed_cases_frame[confirmed_cases_frame['Country']=='China']['Confirmed'],
                                            name='World',
                                            mode='lines')
                                       ],
                                'layout':{
                                    'title':{ 'text':'Time Line of confirmed cases'},
                                    'plot_bgcolor': colors['backgroundconfirmed'],
                                    'paper_bgcolor': colors['plotbackground'],
                                    'font': {'color': colors['textconfirmed']},
                                    'margin': '10px',
                                        'padding': '20px',
                                        'style': {  'width': '60%',
                                                    'height': '40px',
                                                    'border': '5px solid orange',
                                                    'borderWidth': '5px',
                                                    'borderStyle': 'solid',
                                                    'borderRadius': '5px',
                                                    'textAlign': 'center' 
                                               }           
                                       }
                                }
                            )  
                    ],style={'width': '100%','backgroundColor': colors['background']}
                ),

           ]),
])
# Call Back function for timeline_confirmed_cases
@app.callback(
    dash.dependencies.Output('timeline_confirmed_cases', 'figure'),
    [dash.dependencies.Input('countries-menu', 'value')])
def update_graph(country):   
    
    

    
    data=[]
    for i in country:
        temp9=confirmed_cases_frame[confirmed_cases_frame['Country']==i]
        temp9['Dates']=pd.to_datetime(temp9['Dates'])

        data.append(go.Scatter(x=temp9['Dates'],
                            y=temp9['Confirmed'],
                            name=i,
                            hoverinfo="none",
                           hovertext=confirmed_cases_frame[confirmed_cases_frame['Country']==i]['Confirmed'],
                            hovertemplate='<br><b>Confirmed </b>: %{y}<br>'+'<br><b>Date </b>: %{x} <br>',
                            line= {'width':4},mode='lines',
                        #    hovertemplate='<b>%{text}</b>'
                            ))
    
    return {
             'data': data,
            'layout':   {
                                    'title':{ 'text':'Time line of confirmed cases'},
                                    'plot_bgcolor': colors['plotbackground'],
                                    'paper_bgcolor': colors['plotbackground'],
                                    'font': {'color': colors['textrateofraise']},
                                    'xaxis': { 'gridcolor': "#636363", "showline": False},
                                    'margin': '20px',
                                        'padding': '40px',   
                                        'style': {  'width': '100%',
                                                    'height': '30px',
                                                    'border': '5px solid orange',
                                                    'borderWidth': '5px',
                                                    'borderStyle': 'solid',
                                                    'borderRadius': '5px',
                                                    'textAlign': 'center' 
                                               }           
                                       }
                }   
             
        

# Call Back function for timeline_deaths
@app.callback(
    dash.dependencies.Output('timeline_deaths', 'figure'),
    [dash.dependencies.Input('countries-menu', 'value')])
def update_graph(country):
    data=[]
    for i in country:      
        data.append(go.Scatter(x=deaths_cases_frame[deaths_cases_frame['Country']==i]['Dates'],
                            y=deaths_cases_frame[deaths_cases_frame['Country']==i]['Deaths'],
                            name=i,
                            hoverinfo='x+y',
                            hovertext=deaths_cases_frame[deaths_cases_frame['Country']==i]['Deaths'],
                            hovertemplate='<br><b>Deaths </b>: %{y}<br>'+'<br><b>Date </b>: %{x} <br>',
                            line= {'width':4},
                            mode='lines'))
    
    return {
        'data': data,
        'layout':    {
                                    'title':{ 'text':'Time line of deaths'},
                                    'plot_bgcolor': colors['plotbackground'],
                                    'paper_bgcolor': colors['plotbackground'],
                                    'font': {'color': colors['textrateofraise']},
                                    'xaxis': { 'gridcolor': "#636363", "showline": False},
                                    'margin': '20px',
                                     'padding': '40px',  
                                        'style': {  'width': '100%',
                                                    'height': '30px',
                                                    'border': '5px solid orange',
                                                    'borderWidth': '5px',
                                                    'borderStyle': 'solid',
                                                    'borderRadius': '5px',
                                                    'textAlign': 'center' 
                                               }           
                                       }
            }          

# Call Back function for timeline_recovered_cases
@app.callback(
    dash.dependencies.Output('timeline_recovered_cases', 'figure'),
    [dash.dependencies.Input('countries-menu', 'value')])
def update_graph(country):
    data=[]
    for i in country:
        data.append(go.Scatter(x=recovered_cases_frame[recovered_cases_frame['Country']==i]['Dates'],
                                y=recovered_cases_frame[recovered_cases_frame['Country']==i]['Recovered'],
                            name=i,
                            line= {'width':4},
                            hoverinfo='x+y',
                            hovertext=recovered_cases_frame[recovered_cases_frame['Country']==i]['Recovered'],
                            hovertemplate='<br><b>Recovered </b>: %{y}<br>'+'<br><b>Date </b>: %{x} <br>',
                            mode='lines'))
    return {
    'data': data,
    'layout':  {
                                    'title':{ 'text':'Time line of recovered cases'},
                                    'plot_bgcolor': colors['plotbackground'],
                                    'paper_bgcolor': colors['plotbackground'],
                                    'font': {'color': colors['textrateofraise']},
                                    'xaxis': { 'gridcolor': "#636363", "showline": False},
                                    'margin': '20px',
                                        'padding': '40px',   
                                        'style': {  'width': '100%',
                                                    'height': '30px',
                                                    'border': '5px solid blue',
                                                    'borderWidth': '5px',
                                                    'borderStyle': 'solid',
                                                    'borderRadius': '5px',
                                                    'textAlign': 'center' 
                                               }           
                                       }
            }                   
        

# Call Back function for Rate of Spread 
@app.callback(
    dash.dependencies.Output('rate_of_spread_plot', 'figure'),
    [dash.dependencies.Input('countries-menu', 'value')])
def update_graph(country_name):
    data=[]
    for i in country_name:

        temp=confirmed_cases_frame[confirmed_cases_frame['Country']==i][['Dates','Confirmed']]
        temp['Dates']=pd.to_datetime(temp['Dates'],format='%Y-%m-%d')
        temp=temp.set_index('Dates')
        temp=temp.diff()
        temp.dropna(inplace=True)
        rate_of_increase_sampled=temp.resample('D').interpolate()[::7]

        data.append(go.Scatter(x=rate_of_increase_sampled.index,
                                                y=rate_of_increase_sampled['Confirmed'], 
                                                name=i,
                                                line={ 'width':4},  
                                                marker={'size':10}))
    return {
    'data': data,
    'layout':{
                                    'title':{ 'text':'Rate of increase in confirmed cases'},
                                    'plot_bgcolor': colors['plotbackground'],
                                        'paper_bgcolor': colors['plotbackground'],
                                        'font': {'color': colors['textrateofraise']},
                                        'yaxis': { 'gridcolor': "#636363", "showline": False},
                                        'xaxis': { 'gridcolor': "#636363", "showline": False},
                                        'style': {  'width': '100%',
                                                    'height': '60px',
                                                    'lineHeight': '60px',
                                                    'borderWidth': '5px',
                                                    'borderStyle': 'dashed',
                                                    'borderRadius': '5px',
                                                    'textAlign': 'center',
                                                    'margin': '10px'
                                                
                                               }           
                                       }         
        }

# Call Back function for pie chart
@app.callback(
    dash.dependencies.Output('ratio_of_cases', 'figure'),
    [dash.dependencies.Input('countries-menu', 'value')])

def update_graph(single_country):
   

    deaths=deaths_max_date[deaths_max_date['Country'].isin(single_country)]['Deaths'].sum()
    recovered=recovered_max_date[recovered_max_date['Country'].isin(single_country)]['Recovered'].sum()
    confirmed=confirmed_max_date[confirmed_max_date['Country'].isin(single_country)]['Confirmed'].sum()
   
    labels=['Confirmed','Recovered','Deaths']
    values=[confirmed,recovered,deaths]
    

    return {
    'data': [go.Pie(labels=labels,
                    values=values,hole=0.5,
                    textfont=dict(size=20),
                    opacity=1,
                    marker={'colors':colors['pie_colors'],    
                            'line':{'color':colors['text']},
                            },
                    
                                     
                    )],
    'layout':  {     'title':'Proportion of recovery, deaths and confirmed cases',
                                        'plot_bgcolor': colors['plotbackground'],
                                        'paper_bgcolor': colors['plotbackground'],
                                        'font': {'color': colors['text']},
                                         'margin-right': '40px',
                                        'style': {  'width': '40%',
                                                    'height': '60px',
                                                    'borderWidth': '1px',
                                                    'borderStyle': 'dashed',
                                                    'borderRadius': '5px',
                                                    'textAlign': 'center',
                                                    'margin-right': '400px'
                                                }
                }            
        }


# Callback for Map

@app.callback(
    dash.dependencies.Output('world-map', 'figure'),
    [ dash.dependencies.Input('interval', 'n_intervals')
    ])
def update_word_map(interval):
     
    map_text=confirmed_cases_timeline[confirmed_cases_timeline['Date_id']<=interval]['Country']
    latitude=confirmed_cases_timeline[confirmed_cases_timeline['Date_id']<=interval]['latitude']
    longitudes=confirmed_cases_timeline[confirmed_cases_timeline['Date_id']<=interval]['longitudes']

    map_data = [
      {
        "type": "scattermapbox",
        "lat": [0.1],
        "lon": [0.1],
        "hoverinfo": "text",
        "text": "text",  
        "mode": "lines",
        "line": {"color": colors['plotbackground']},
    },
    {
        "type": "scattermapbox",
        "lat": latitude,
        "lon": longitudes,
        "hoverinfo": "text+lon+lat",
        "text": map_text,
        "mode": "scattermapbox",
        "marker": {"size": 10, "color": colors['mapmarkers']}
    },
        ]

    map_layout = {
        "mapbox": {
        "accesstoken": MAPBOX_ACCESS_TOKEN,
        "style": MAPBOX_STYLE,
         "center": [60.5000209,9.0999715],
         "zoom": 0.9
         },
        "showlegend": False,
        "autosize": True,
        "paper_bgcolor": colors['plotbackground'],
     "plot_bgcolor": colors['plotbackground'],
     "margin": {"t": 0, "r": 20, "b": 0, "l": 0},
    }
    
    return {
            'data': map_data,
            'layout':   map_layout        
            }

if __name__ == '__main__':
    app.run_server(debug=False)  