import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_gif_component as gif
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_table
import pandas as pd 
import numpy as np
import datetime 
import time
import warnings
import os
import plotly.express as px
import plotly.graph_objs as go
import newsapi
import smtplib
from newsapi.newsapi_client import NewsApiClient



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
    'pie_colors' : ['#728C00','#018d61','#d40000'],
    'tabbackground':'#808080',
    'seltabbackground':'#303030'
}

MAPBOX_ACCESS_TOKEN = "pk.eyJ1Ijoic2FudG9zaGNiaXQyMDAyIiwiYSI6ImNrODhrM2V3djA4djAzcXFhanh2eHpiM20ifQ.X9kcJYiDV41QidY4DgYVcA"
MAPBOX_STYLE="mapbox://styles/santoshcbit2002/ck88qasdh2dpe1ip5io9mauu9"


data_source_text='Data Source : John Hopkins University, USA.'
data_refresh_text='Last Data refresh : ' + str(datetime.datetime.now().date()-datetime.timedelta(days=1))

copy_right_text1= "Built by: www.linkedin.com/in/santoshambaprasad/"
copy_right_text2= "          www.linkedin.com/in/bhargavikanchiraju/"

#confirmed_cases_ps=

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
# Plots 4 and 6
confirmed_max_date=pd.read_csv('pre_processed_confirmed_max_date.csv')
recovered_max_date=pd.read_csv('pre_processed_recovered_max_date.csv')
deaths_max_date=pd.read_csv('pre_processed_deaths_max_date.csv')

# Previous day files 
confirmed_max_date_minus_one_day=pd.read_csv('pre_processed_confirmed_max_date_minus_one_day.csv')
recovered_max_date_minus_one_day=pd.read_csv('pre_processed_recovered_max_date_minus_one_day.csv')
deaths_max_date_minus_one_day=pd.read_csv('pre_processed_deaths_max_date_minus_one_day.csv')


# Animation file
combined_frame_master=pd.read_csv('pre_processed_combined_frame_master.csv')

print('pre_processed_confirmed_cases - data read complete. Shape of data {}'.format(confirmed_cases_frame.shape))
print('pre_processed_recovered_cases - data read complete. Shape of data {}'.format(recovered_cases_frame.shape))
print('pre_processed_deaths_cases - data read complete. Shape of data {}'.format(deaths_cases_frame.shape))
print('pre_processed_confirmed_max_date - data read complete. Shape of data {}'.format(confirmed_max_date.shape))
print('pre_processed_recovered_max_date - data read complete. Shape of data {}'.format(recovered_max_date.shape))
print('pre_processed_deaths_max_date - data read complete. Shape of data {}'.format(deaths_max_date.shape))


print('-'*50)

confirmed_max_date['Confirmed_text']=confirmed_max_date['Confirmed'].astype(str)
confirmed_max_date['Confirmed_text']=confirmed_max_date['Confirmed_text'].apply(lambda x: ' :'+x)
confirmed_max_date['text_hover']=confirmed_max_date['Country']+confirmed_max_date['Confirmed_text']

confirmed_cases=confirmed_max_date['Confirmed'].sum()
recovered_cases=recovered_max_date['Recovered'].sum()
deaths_cases=deaths_max_date['Deaths'].sum()

###################################################################
# Prepare Data for Confirmed Cases Pie Graph                      #
################################################################### 

top9_confirmed=confirmed_max_date.sort_values(by='Confirmed',ascending=False).head(9)
top9_confirmed_countries=list(top9_confirmed['Country'].unique())
values_confirmed=list(top9_confirmed['Confirmed'])

rest_confirmed=confirmed_max_date[~confirmed_max_date['Country'].isin(top9_confirmed_countries)]
rest_confirmed_cases=rest_confirmed['Confirmed'].sum()

top9_confirmed_countries.append('Rest')
labels_confirmed=top9_confirmed_countries
values_confirmed.append(rest_confirmed_cases)

###################################################################
# Prepare Data for Recovered Cases Pie Graph                      #
################################################################### 

top9_recovered=recovered_max_date.sort_values(by='Recovered',ascending=False).head(9)
top9_recovered_countries=list(top9_recovered['Country'].unique())
values_recovered=list(top9_recovered['Recovered'])

rest_recovered=recovered_max_date[~recovered_max_date['Country'].isin(top9_recovered_countries)]
rest_recovered_cases=rest_recovered['Recovered'].sum()

top9_recovered_countries.append('Rest')
labels_recovered=top9_recovered_countries
values_recovered.append(rest_recovered_cases)

###################################################################
# Prepare Data for Deaths Pie Graph                               #
################################################################### 

top9_deaths=deaths_max_date.sort_values(by='Deaths',ascending=False).head(9)
top9_deaths_countries=list(top9_deaths['Country'].unique())
values_deaths=list(top9_deaths['Deaths'])

rest_deaths=deaths_max_date[~deaths_max_date['Country'].isin(top9_deaths_countries)]
rest_deaths_cases=rest_deaths['Deaths'].sum()

top9_deaths_countries.append('Rest')
labels_deaths=top9_deaths_countries
values_deaths.append(rest_deaths_cases)


###################################################################
# Prepare functions for emailing                                  #
################################################################### 

def sendemail(from_addr, to_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587', cc_addr_list=[]):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
 
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return problems

def triggeremail(message_txt):    
     sendemail(from_addr    = 'dashboardstest2020@gmail.com', 
          to_addr_list = ['bhargavi.sivapurapu@gmail.com','santosh.cbit2002@gmail.com'],
          subject      = 'COVID19 DashBoard User Feedback', 
          message      = message_txt, 
          login        = 'dashboardstest2020@gmail.com', 
          password     = 'offbduwbzbrizdrg') 
    

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
# Prepare Data for Rate of spread graph                             #
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
confirmed=confirmed-recovered-deaths

values=[confirmed,recovered,deaths]


###################################################################
# Prepare Data for World Statistic                                #
################################################################### 

confirmed_cases=confirmed_max_date['Confirmed'].sum()
recovered_cases=recovered_max_date['Recovered'].sum()
deaths_cases=deaths_max_date['Deaths'].sum()

previous_day_confirmed_cases=confirmed_max_date_minus_one_day['Confirmed'].sum()
previous_day_recovered_cases=recovered_max_date_minus_one_day['Recovered'].sum()
previous_day_deaths_cases=deaths_max_date_minus_one_day['Deaths'].sum()


confirmed_cases_text=str(confirmed_cases) + ' ('+'{:+.0f}'.format(confirmed_cases-previous_day_confirmed_cases) + ')'
recovered_cases_text=str(recovered_cases) + ' ('+'{:+.0f}'.format(recovered_cases-previous_day_recovered_cases) + ')'
deaths_cases_text=str(deaths_cases) + ' ('+'{:+.0f}'.format(deaths_cases-previous_day_deaths_cases) + ')'

confirmed_cases_card_content = [
    dbc.CardHeader("Confirmed Cases"),
    dbc.CardBody(
        [
            html.H5(confirmed_cases_text, className="card-title")
            
        ]
    ),
]

recovered_cases_card_content = [
    dbc.CardHeader("Recovered Cases"),
    dbc.CardBody(
        [
            html.H5(recovered_cases_text, className="card-title")
            
        ]
    ),
]

deaths_card_content = [
    dbc.CardHeader("Deaths\t\t"),
    dbc.CardBody(
        [
            html.H5(deaths_cases_text, className="card-title")
            
        ]
    ),
]

previous_day_confirmed_cases_card_content = [
    dbc.CardHeader("Previous day confirmed cases "),
    dbc.CardBody(
        [
            html.H5(previous_day_confirmed_cases, className="card-title")
            
        ]
    ),
]

previous_day_recovered_cases_card_content = [
    dbc.CardHeader("Previous day recovered cases"),
    dbc.CardBody(
        [
            html.H5(previous_day_recovered_cases, className="card-title")
            
        ]
    ),
]

previous_day_deaths_card_content = [
    dbc.CardHeader("Previous day deaths"),
    dbc.CardBody(
        [
            html.H5(previous_day_deaths_cases, className="card-title")
            
        ]
    ),
]

###################################################################
# Prepare Data for Map                                            #
################################################################### 

# Get data for Map
id=0

max_interval_count=len(confirmed_max_date)

map_fig = go.Figure(go.Scattermapbox(
        lat=confirmed_max_date['latitude'],
        lon=confirmed_max_date['longitudes'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color='#B20000'
        ),
        text=confirmed_max_date['text_hover'],
        hovertext=confirmed_max_date['text_hover'],
        hoverinfo='text'
    ))

map_fig.update_layout(
    hovermode='closest',
    paper_bgcolor=colors['plotbackground'],
    plot_bgcolor=colors['plotbackground'],
    margin={"t": 2, "r": 0, "b": 2, "l": 0},
 #   width=1600,
   height=600, 
    showlegend=False,
    autosize= True,
    mapbox=dict(
        accesstoken=MAPBOX_ACCESS_TOKEN,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=19.998,
            lon=7.032
        ),       
        style=MAPBOX_STYLE,
        zoom=1.0
    ),
)

dashboard_world_map=html.Div( dcc.Graph(id="world-map",config={'staticPlot': False},style={'width':'100%'},
                                    figure=map_fig)),

###################################################################
#       Prepare data for News                                     #
###################################################################
newsapi_obj = NewsApiClient(api_key='e233bbffef0a42279c871476d6772e8f')
top_headlines = newsapi_obj.get_top_headlines(q='corona',
                            sources='bbc-news,Google News (UK),Independent,FourFourTwo',
                            # sources='bbc-news',
                                          language='en') 

source_name=[]
url_text=[]
new_title=[]
published=[]

for i in range(0,top_headlines['totalResults']):
    source_name.append(top_headlines['articles'][i]['source']['name'])
    new_title.append(top_headlines['articles'][i]['title'])
    url_text.append(top_headlines['articles'][i]['url'])  
    published.append(top_headlines['articles'][i]['publishedAt'])

news_item=[]
for i in range(0,len(new_title)):
    news_item.append(dbc.ListGroupItem(new_title[i],href=url_text[i],color=colors['text']))

dashboard_news_table=html.Div(
                             dbc.Card([
                                        dbc.Alert('Top Headlines',color='warning'),
                                        dbc.ListGroup(news_item, flush=True)
                                        ],
                            outline=True), style={'width':'60%','margin-left':'20px'},
)

################################################################### 
# Prepare feedback layout                                         #
################################################################### 


feedback_def_value='Please leave feedback here. Please leave your contact, if you wish to be contacted. Thank you :-)'


dashboard_feedback_area = dbc.Container([ dbc.FormGroup([  html.Br(),
                                                           dbc.Input(id="text-area", placeholder='', type="text",bs_size=5),
                                                           dbc.FormText(feedback_def_value,color='warning',
                                                                        style={ 'font-size':'120%',
                                                                                'font-family':'Open Sans', 
                                                                                'font-weight': 'normal'
                                                                        }),
                                                           html.Br(),
                                                           dbc.Button("Submit", color="primary", id='submit-button',className="mr-2"),
                                                           html.P(id="output",style={'color':'#ff7518'})
                                                            ])
                                            ])


#######################################################################
#             Create animation App                                    #
#######################################################################

date_list=list(confirmed_cases_frame['Dates'].unique())
date_list=date_list[0:-1:1]
f=pd.DataFrame()
for i in date_list:
    fx=confirmed_cases_frame[confirmed_cases_frame['Dates']==i].sort_values(by='Confirmed',ascending=False).head(10)
    f=f.append(fx)
f['Day']=f['Dates'].astype(str)
max_range=f['Confirmed'].max()


#y_axis_category='Confirmed Cases (Scaled for purpose of graph)'
#y_axis_category='Confirmed Cases'
#combined_frame_master_selected=combined_frame_master[combined_frame_master['Country'].isin(['India','US','United Kingdom','Italy','Spain'])]
#y_max_range=combined_frame_master_selected[y_axis_category].max()
#y_max_range=y_max_range+0.05*y_max_range

animation_fig = px.bar(f, x="Country", 
                          y="Confirmed",
                          animation_group='Country',
                          animation_frame="Day",
                          range_y=[0,max_range+10000],
                          color_discrete_sequence=px.colors.qualitative.Plotly,
                          template='plotly_dark',
                          title='Rise of cases with respect to time',
                          labels={'Country':' ','Confirmed':'Confirmed Cases'}
                        )

#animation_fig=px.bar(combined_frame_master_selected, y="Country", x=y_axis_category, color="Country",   orientation='h',
#  title='Rise of cases(scaled) with respect to time (Y axis is scaled in the graph. Refer map for confirmed cases)',
#  animation_frame="Dates", animation_group="Country",range_x=[0,y_max_range],template='plotly_dark')

animation_fig.update_layout(font=dict(color=colors['text'], size=12),
                            plot_bgcolor=colors['plotbackground'],
                            paper_bgcolor=colors['plotbackground'])
animation_fig.update_xaxes(tickangle=20, tickfont=dict(family='Open Sans', color=colors['text'], size=15))

dashboard_animation_plot=html.Div(
                            [   
                                dcc.Graph( id='animation_plot_area',    
                                figure=animation_fig)
                            ],style={'backgroundColor': colors['plotbackground']})

###################################################################
# Prepare html layout components                                  #
################################################################### 

santosh_ln= html.Div( [ 
            dcc.Link('https://www.linkedin.com/in/santoshambaprasad/',href='https://www.linkedin.com/in/santoshambaprasad/',
             style={
                'textAlign': 'right', 
                'backgroundColor':colors['plotbackground'],
                'padding': '1px',
                'color': colors['text'],
                'font-size':'100%',
                'font-family':'Open Sans', 
                'font-weight': 'normal',
                'letter-spacing': 0.5,
                'margin-left': '3px'}     
            )
            ])


bhargavi_ln=html.Div( [ 
            dcc.Link('https://www.linkedin.com/in/bhargavikanchiraju/',href='https://www.linkedin.com/in/bhargavikanchiraju/',
            style={
                'text-align': 'right', 
                'backgroundColor':colors['plotbackground'],
                'padding': '1px',
                'color': colors['text'],
                'font-size':'100%',
                'font-family':'Open Sans', 
                'font-weight': 'normal',
                'letter-spacing': 0.5,
                'margin-left': '3px'}     
                ) 
            ]
            )

dashboard_title=html.H2(
            style={
            'textAlign': 'center', 
           # 'backgroundColor':colors['plotbackground'],
            'padding': '12px',
            'color': colors['text'],
            'font-size':'300%',
            'font-family':'Open Sans', 
            'font-weight': 'normal',
            'letter-spacing': 1.0,
 
            'margin': 0},
            children='COVID - 19 Dashboard'

            )

dashboard_source_text=html.Div( style={},
            children=[
            html.H3(
                    children=data_source_text,
                     style={
                        'textAlign': 'right', 
         #               'backgroundColor':colors['plotbackground'],
                        'color': colors['text'],
                        'font-size':'100%',
                        'font-family':'Open Sans', 
                        'font-weight': 'normal',
                        'letter-spacing': 0.2
                        },
                    )   
            ])

dashboard_refresh_text=html.Div( style={},
            children=[
            html.H3(
                    children=data_refresh_text,
                     style={
                        'textAlign': 'right', 
          #              'backgroundColor':colors['plotbackground'],
                        'color': colors['text'],
                        'font-size':'100%',
                        'font-family':'Open Sans', 
                        'font-weight': 'normal',
                        'letter-spacing': 0.2
                        },
                    )   
            ])

dashboard_menu=html.Div(
            [ html.Div([
                html.Label( 
                [
                 "Select upto 3 Countries",
                        dcc.Dropdown(
                        id='countries-menu',
                        options=menu_dict_list,
                        value=['US','Brazil','India'],
                        placeholder="Select Countries",
                        multi=True
                                ),
                            ])
                 ])],
                style={'width': '40%', 
                        'backgroundColor': colors['plotbackground'],
                        'margin-bottom': '30px',
                        'color': colors['text'],
                        'font-size':'100%',
                        'font-family':'Open Sans', 
                        'font-weight': 'normal',
                        }
                )

dashboard_map_text=html.Div( style={'backgroundColor': colors['plotbackground']},
                 children=[
                    html.H4(
                        children='Confirmed cases across the globe',
                        style={
                                'textAlign': 'right', 
                                'margin-right' : '160px',
                                'backgroundColor':colors['plotbackground'],
                                'color': colors['text'],
                                'font-size':'140%',
                                'font-family':'Open Sans', 
                                'font-weight': 'normal',
                                'letter-spacing': 0.2,
                                'margin-bottom':'0px'
                             },
                        )   
                        ])

dashboard_rate_of_raise=html.Div([   
                        dcc.Graph( id='rate_of_spread_plot',
                        figure={
                                'data': [
                                        go.Scatter(x=rate_of_increase_sampled.index,
                                        y=rate_of_increase_sampled['Confirmed'], 
                                        line={'color':colors['mapmarkers'], 'width':4},
                                        marker={'size':10})
                                        ],
                                'layout':{
                                        'title':{ 'text':'Rate of spread weekly) in confirmed cases'},
                                        'plot_bgcolor': colors['plotbackground'],
                                        'paper_bgcolor': colors['plotbackground'],
                                        'font': {'color': colors['textrateofraise']},
                                        'yaxis': { 'gridcolor': "#636363", "showline": False},
                                        'xaxis': { 'gridcolor': "#636363", "showline": False},
                                        'style': {  'width': '100%',
                                        'lineHeight': '60px',
                                        'borderWidth': '5px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                        'margin': '10px'}           
                                                     }
                                                }
                                            )  
                                    ],
                                    style={'width': '100%',
                                           'backgroundColor': colors['plotbackground']                           
                                    }
                            )

dashboard_copyright_stmt= html.Div(
                        dcc.Markdown(
                        '''
                         News headlines powered by NewsAPI.org
                        '''
                        ),
                        style={
                        'textAlign': 'center', 
                        'backgroundColor':colors['plotbackground'],
                        'color': colors['text'],
                        'font-size':'100%',
                        'margin-top':'20px',
                        'font-family':'Open Sans', 
                        'font-weight': 'normal'
                       
                        },
                                    )


dashboard_deaths_chart= html.Div([
                    dcc.Graph(
                        id='timeline_deaths',
                        figure={
                                'data': [
                                    go.Scatter(x=deaths_cases_frame[deaths_cases_frame['Country']=='China']['Dates'],
                                                y=deaths_cases_frame[deaths_cases_frame['Country']=='China']['Deaths'],
                                                name='China',stackgroup='one',
                                                mode='lines')
                                       ],
                                'layout': {
                                    'title':{ 'text':'Timeline of deaths'},
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
                   style={'backgroundColor': colors['plotbackground']
                        }  
                )

dashboard_recovered_chart=html.Div([   
                   dcc.Graph(
                        id='timeline_recovered_cases',
                        figure={
                                'data': [
                                    go.Scatter(x=recovered_cases_frame[recovered_cases_frame['Country']=='China']['Dates'] ,
                                    y=recovered_cases_frame[recovered_cases_frame['Country']=='China']['Recovered'],
                                                name='China',stackgroup='one',
                                                mode='lines')
                                       ],
                                'layout': {
                                    'title':{ 'text':'Timeline of recovered cases'},
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

dashboard_pie_chart=html.Div([   
                            dcc.Graph(
                            id='ratio_of_cases',
                            figure={
                                'data':  [
                                    go.Pie(labels=labels,
                                        values=values,hole=0.5)
                                       ],  
                                'layout':{
                                    'title':'Recovery and Deaths as a % of confirmed cases',
                                    'plot_bgcolor': colors['plotbackground'],
                                        'paper_bgcolor': colors['plotbackground'],
                                        'font': {'color': colors['textrateofraise']},
                                         "margin": {"t": 0, "r": 0, "b": 0, "l": 0},
                                         'legend_orientation':'h',
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
                        style={'width': '80%','backgroundColor': colors['plotbackground'],'margin-left': '40px'}
                        )

dashboard_pie_chart_confirmed_cases=html.Div([   
                            dcc.Graph(
                            id='ratio_of_confirmed_cases',
                            figure={
                                'data':  [
                                    go.Pie(labels=labels_confirmed,
                                        values=values_confirmed,hole=0.5)
                                       ],  
                                'layout':{
                                    'title':'Spread of total confirmed cases ',
                                   'plot_bgcolor': colors['plotbackground'],
                                        'paper_bgcolor': colors['plotbackground'],
                                        'font': {'color': colors['textrateofraise']},
                                         "margin": {"t": 50, "r": 0, "b": 20, "l": 0},
                                         'legend_orientation':'h',
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
                        style={'width': '80%','backgroundColor': colors['plotbackground']}
                        )

dashboard_pie_chart_recovered_cases=html.Div([   
                            dcc.Graph(
                            id='ratio_of_recovered_cases',
                            figure={
                                'data':  [
                                    go.Pie(labels=labels_recovered,
                                        values=values_recovered,hole=0.5)
                                       ],  
                                'layout':{
                                    'title':'Spread of total recovered cases ',
                                      'plot_bgcolor': colors['plotbackground'],
                                        'paper_bgcolor': colors['plotbackground'],
                                        'font': {'color': colors['textrateofraise']},
                                         "margin": {"t": 50, "r":0, "b": 20, "l": 0},
                                         'legend_orientation':'h',
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
                        style={'width': '80%','backgroundColor': colors['plotbackground']}
                        )

dashboard_pie_chart_death_cases=html.Div([   
                            dcc.Graph(
                            id='ratio_of_death_cases',
                            figure={
                                'data':  [
                                    go.Pie(labels=labels_deaths,
                                        values=values_deaths,hole=0.5)
                                       ],  
                                'layout':{
                                    'title':'Spread of total deaths ',
                                    'plot_bgcolor': colors['plotbackground'],
                                        'paper_bgcolor': colors['plotbackground'],
                                        'font': {'color': colors['textrateofraise']},
                                         "margin": {"t": 50, "r": 0, "b": 20, "l": 0},
                                         'legend_orientation':'h',
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
                        style={'width': '80%','backgroundColor': colors['plotbackground']}
                        )

dashboard_confirmedcases_chart=html.Div([   
                        dcc.Graph(
                            id='timeline_confirmed_cases',
                            figure={
                                'data': [
                                    go.Scatter(x=confirmed_cases_frame[confirmed_cases_frame['Country']=='China']['Dates'],
                                            y=confirmed_cases_frame[confirmed_cases_frame['Country']=='China']['Confirmed'],
                                            name='World',stackgroup='one',
                                            mode='lines')
                                       ],
                                'layout':{
                                    'title':{ 'text':'Timeline of confirmed cases'},
                                    'plot_bgcolor': colors['plotbackground'],
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
                    ],style={'width': '100%','backgroundColor': colors['plotbackground']}
                )

dashboard_animation_gif=html.Div([   
                        gif.GifPlayer(
                        gif='assets/animation.gif',
                        still='assets/animation.png',
                    )
                                     
                    ],style={'width': '100%','backgroundColor': colors['background']}
                )



##############################################################################
#                               Create DASH App instance                     #
##############################################################################

app = dash.Dash(external_stylesheets=[dbc.themes.CYBORG])

server=app.server

##############################################################################
#                               HTML Layout                                  #
##############################################################################

app.layout = html.Div(
         style={'backgroundColor': colors['plotbackground']
      #             'background-size': '800px 500px' 
           },
    children=[

           	dbc.Row(dbc.Col(santosh_ln)),
		    dbc.Row(dbc.Col(bhargavi_ln)),
            dbc.Row(dbc.Col(dashboard_title)),
        	dbc.Row(dbc.Col(dashboard_source_text)),
		    dbc.Row(dbc.Col(dashboard_refresh_text)),
 
            
            dbc.Row( [
                dbc.Col(dashboard_world_map),
                dbc.Col(
                     html.Div(
                         children=[
                                html.Br(),
                                dbc.Row([
                                    dbc.Col(dbc.Card(confirmed_cases_card_content,color='warning',inverse=True)),
                                    dbc.Col(dbc.Card(previous_day_confirmed_cases_card_content,color='warning',inverse=True))
                                    ]),
                                html.Br(),
                                dbc.Row([
                                    dbc.Col(dbc.Card(recovered_cases_card_content,color='success',inverse=True)),
                                    dbc.Col(dbc.Card(previous_day_recovered_cases_card_content,color='success',inverse=True))
                                    ]), 
                                html.Br(),
                                dbc.Row([
                                    dbc.Col(dbc.Card(deaths_card_content,color='danger',inverse=True)),
                                    dbc.Col(dbc.Card(previous_day_deaths_card_content,color='danger',inverse=True))
                                    ]),
                                    ],
                            style={'margin-right':'30px',
                                   'font-size':'105%',
                                   'font-family':'Open Sans', 
                                   'font-weight': 'normal'
                                    })
                        ),
                    ]),
               
            
            dbc.Row(dbc.Col(dashboard_animation_plot)),

             dbc.Row( [
                        dbc.Col(html.Div(dashboard_pie_chart_confirmed_cases)),
                        dbc.Col(html.Div(dashboard_pie_chart_recovered_cases)),
                        dbc.Col(html.Div(dashboard_pie_chart_death_cases))
                        ]
                    ),


           # dbc.Row([dbc.Col(dashboard_animation_gif)]),
           
            dbc.Row(dbc.Col(dashboard_menu)),

            dbc.Row(dbc.Col(dashboard_rate_of_raise)),
            
            dbc.Row( [
                        dbc.Col(html.Div(dashboard_deaths_chart)),
                        dbc.Col(html.Div(dashboard_recovered_chart))
                        ]
                    ),

            dbc.Row( [
                        dbc.Col(html.Div(dashboard_pie_chart)),
                        dbc.Col(html.Div(dashboard_confirmedcases_chart))
                        ]
                    ),

            dbc.Row(dashboard_news_table,justify='center'),
            
            dashboard_feedback_area,
            
            dashboard_copyright_stmt
                    
    ])


# Call Back function for timeline_confirmed_cases   
@app.callback(
    dash.dependencies.Output('timeline_confirmed_cases', 'figure'),
    [dash.dependencies.Input('countries-menu', 'value')])
def update_graph(country):   
    
    country=country[0:3]
    data=[]
    for i in country:
        temp9=confirmed_cases_frame[confirmed_cases_frame['Country']==i]
        temp9['Dates']=pd.to_datetime(temp9['Dates'])

        data.append(go.Scatter(x=temp9['Dates'],
                            y=temp9['Confirmed'],
                            name=i,
                            hoverinfo="none",
                            stackgroup='one',
                           hovertext=confirmed_cases_frame[confirmed_cases_frame['Country']==i]['Confirmed'],
                            hovertemplate='<br><b>Confirmed </b>: %{y}<br>'+'<br><b>Date </b>: %{x} <br>',
                            line= {'width':4},mode='lines',
                        #    hovertemplate='<b>%{text}</b>'
                            ))
    
    return {
             'data': data,
            'layout':   {
                                    'title':{ 'text':'Timeline of confirmed cases'},
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
    country=country[0:3]
    for i in country:      
        data.append(go.Scatter(x=deaths_cases_frame[deaths_cases_frame['Country']==i]['Dates'],
                            y=deaths_cases_frame[deaths_cases_frame['Country']==i]['Deaths'],
                            name=i,
                            hoverinfo='x+y',
                            stackgroup='one',
                            hovertext=deaths_cases_frame[deaths_cases_frame['Country']==i]['Deaths'],
                            hovertemplate='<br><b>Deaths </b>: %{y}<br>'+'<br><b>Date </b>: %{x} <br>',
                            line= {'width':4},
                            mode='lines'))
    
    return {
        'data': data,
        'layout':    {
                                    'title':{ 'text':'Timeline of deaths'},
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
    country=country[0:3]
    for i in country:
        data.append(go.Scatter(x=recovered_cases_frame[recovered_cases_frame['Country']==i]['Dates'],
                                y=recovered_cases_frame[recovered_cases_frame['Country']==i]['Recovered'],
                            name=i,
                            line= {'width':4},
                            hoverinfo='x+y',
                            stackgroup='one',
                            hovertext=recovered_cases_frame[recovered_cases_frame['Country']==i]['Recovered'],
                            hovertemplate='<br><b>Recovered </b>: %{y}<br>'+'<br><b>Date </b>: %{x} <br>',
                            mode='lines'))
    return {
    'data': data,
    'layout':  {
                                    'title':{ 'text':'Timeline of recovered cases'},
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
    country_name=country_name[0:3]
    for i in country_name:

        temp=confirmed_cases_frame[confirmed_cases_frame['Country']==i][['Dates','Confirmed']]
        temp['Dates']=pd.to_datetime(temp['Dates'],format='%Y-%m-%d')
        temp=temp.set_index('Dates')
        temp['difference']=temp.diff()
        temp['Confirmed_lag']=temp['Confirmed'].shift(1)
        temp['percentage_increase']=temp['difference']/temp['Confirmed_lag']*100
        temp['percentage_increase']=temp['percentage_increase'].apply(lambda x: round(x,3))
        temp.replace([np.inf, -np.inf], np.nan) 
        temp.dropna(inplace=True)
        rate_of_increase_sampled=temp.resample('D').interpolate()[::3]

        data.append(go.Scatter(x=rate_of_increase_sampled.index,
                                                y=rate_of_increase_sampled['percentage_increase'], 
                                                name=i,
                                                line={ 'width':4},  
                                                marker={'size':10}))
    return {
    'data': data,
    'layout':{
                                    'title':{ 'text':'Rate of spread (weekly) in confirmed cases'},
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
   
    labels=['Confirmed - Excluding Deaths and <br> Recovered cases','Recovered','Deaths']
    confirmed=confirmed-recovered-deaths
    values=[confirmed,recovered,deaths]

    return {
    'data': [go.Pie(labels=labels,
                    values=values,
                    textfont=dict(size=15),
                  #  pull=[0.5,0.5,0],
                    opacity=1,
                    rotation=120,
                    marker={'colors':colors['pie_colors'],    
                            'line':{'color':colors['text']},
                            },
                    
                                     
                    )],
    'layout':  {     'title':'Recovery and Deaths as a % of confirmed cases',
                                        'plot_bgcolor': colors['plotbackground'],
                                        'paper_bgcolor': colors['plotbackground'],
                                        'font': {'color': colors['text']},
                                         'margin-right': '40px',
                                         'legend_orientation':'v',
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

# Call Back function for feedback text
@app.callback(
    [Output('output', 'children'),Output('text-area','value')],
    [Input('submit-button', 'n_clicks')],
    [State('text-area', 'value')]
)
def update_output(button_clicks,value):
        if button_clicks is None:
             button_clicks=0
        
        if button_clicks > 0:
           triggeremail(value)
           return 'Thank you for the feed back',''
        else:
            return '',''

"""

# Call Back function for animation
@app.callback(
    dash.dependencies.Output('animation_plot_area', 'figure'),
    [dash.dependencies.Input('countries-menu', 'value')])

def update_graph(country_selection):   
    combined_frame_master_selected=combined_frame_master[combined_frame_master['Country'].isin(country_selection)]
    y_max_range=combined_frame_master_selected[y_axis_category].max()
    y_max_range=y_max_range+0.05*y_max_range

    animation_fig=px.bar(combined_frame_master_selected, y="Country", x=y_axis_category, color="Country",orientation='h',
      title='Rise of cases(scaled) with respect to time (Y axis is scaled in the graph. Refer map for confirmed cases)',
        animation_frame="Dates", animation_group="Country",range_x=[0,y_max_range],template='plotly_dark')

    animation_fig.update_layout(font=dict(color=colors['text'], size=12))
    
    data=[]
    data.append(px.bar(combined_frame_master_selected, y="Country",
                                    x=y_axis_category, color="Country",orientation='h',
                                    title='',
                                    animation_frame="Dates", animation_group="Country",
                                    range_y=[0,y_max_range],template='plotly_dark'))

    return animation_fig
"""
if __name__ == '__main__':
    app.run_server(debug=True)  