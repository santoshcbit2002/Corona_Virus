import pandas as pd
import numpy as np
import warnings
import time
#from geopy.geocoders import Nominatim
#import datetime
import os
#import geopy
import smtplib
from datetime import datetime,timedelta
#from geopy.geocoders import Nominatim
#from geopy.exc import GeocoderTimedOut

###################################################################
# Initiate Program                                                #
################################################################### 

warnings.filterwarnings("ignore")
print('Current Working Directory : ',os.getcwd())
print('#'*60)
print(' Data Pre-processing Script Started {}'.format(datetime.now()))
process_flag='N'
message_txt=''

###################################################################
# Define  helper functions                                     #
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
          subject      = 'COVID19 DashBoard Data Pull and Pre-Processing Status', 
          message      = message_txt, 
          login        = 'dashboardstest2020@gmail.com', 
          password     = 'offbduwbzbrizdrg') 

###################################################################
# Read the files                                                  #
################################################################### 

confirmed_file='https://raw.github.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
deaths_file='https://raw.github.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
recovered_file='https://raw.github.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
lat_lon_file='https://raw.github.com/santoshcbit2002/santoshcbit2002-Corona_Virus/master/DashBoard/App/lat_lon_data.csv'

try:
    confirmed=pd.read_csv(confirmed_file)
    deaths=pd.read_csv(deaths_file)
    recovered=pd.read_csv(recovered_file)
    lat_lon_data=pd.read_csv(lat_lon_file)
    process_flag='Y' 
    print(' *** All the four source files have been downloaded')

except:
    message_txt='File downloads have failed. Please check'
    triggeremail(message_txt)
    exit(0)

print(' *** Data load completed *** ')

###################################################################
# Clean the Confirmed Cases File                                  #
################################################################### 
# Confirmed Cases Data - Processing
confirmed.drop(columns=['Province/State','Lat','Long'],inplace=True)
cols=list(confirmed)
cols.remove('Country/Region')
confirmed_country_group=confirmed.groupby(['Country/Region'])[cols].sum().reset_index()

print(' *** Data Pre-prossing on confirmed cases completed *** ')

###################################################################
# Clean the Recovery Cases File                                   #
################################################################### 

# Recovery Cases Data - Processing
recovered.drop(columns=['Province/State','Lat','Long'],inplace=True)
cols=list(recovered)
cols.remove('Country/Region')
recovered_country_group=recovered.groupby(['Country/Region'])[cols].sum().reset_index()

print(' *** Data Pre-processing on recovered cases completed *** ')

###################################################################
# Clean the Deaths File                                           #
###################################################################                                 

# Deaths Cases Data - Processing
deaths.drop(columns=['Province/State','Lat','Long'],inplace=True)
cols=list(deaths)
cols.remove('Country/Region')
deaths_country_group=deaths.groupby(['Country/Region'])[cols].sum().reset_index()

print(' *** Data Pre-processing on death cases completed *** ')

###################################################################
# Create the Date file                                            #
###################################################################  
# Create Date list
date_list=list(confirmed_country_group)
date_list.remove('Country/Region')

date_list_formatted=[]
for i in date_list:
    date_list_formatted.append((datetime.strptime(i, '%m/%d/%y')).date().isoformat())

max_date=max(date_list_formatted)

print(' *** Latest Date of the Data: ', max_date)

yesterday=datetime.strftime(datetime.now() - timedelta(2), '%Y-%m-%d')

"""
if  max_date == yesterday:
    process_flag='Y'    
else:
    message_txt= message_txt+'Date update failed'
    print('error-2')
    process_flag='N'
"""

if  process_flag =='Y' :
     message_txt_update='Update has been successful for date : '+str(max_date) + '\n' + 'All the files are saved successfully.'

     triggeremail(message_txt_update)    
else:
    triggeremail(message_txt)

print(' *** Starting the Transformation of Data *** ')

###################################################################
# Transform Confirmed Cases Data                                  #
###################################################################  

countries_list=confirmed_country_group['Country/Region'].unique()
col_tran=list(confirmed_country_group)
col_tran.remove('Country/Region')

confirmed_cases_frame=pd.DataFrame()
for i in  countries_list:
    data_points=confirmed_country_group[confirmed_country_group['Country/Region']==i][col_tran].values
    transformed_data=pd.DataFrame(data={'Country':i,
                      'Dates':col_tran,
                    'Confirmed':data_points[0]})
    confirmed_cases_frame=confirmed_cases_frame.append(transformed_data)

confirmed_cases_frame['Dates']=pd.to_datetime(confirmed_cases_frame['Dates'],format='%m/%d/%y')
confirmed_cases_frame['Dates']=confirmed_cases_frame['Dates'].apply(lambda x:x.date())

print(' *** Transformation of confirmed_cases data completed *** ')

###################################################################
# Transform Recovered Cases Data                                  #
###################################################################  

recovered_list=recovered_country_group['Country/Region'].unique()
col_tran=list(recovered_country_group)
col_tran.remove('Country/Region')

recovered_cases_frame=pd.DataFrame()
for i in  recovered_list:
    data_points=recovered_country_group[recovered_country_group['Country/Region']==i][col_tran].values
    transformed_data=pd.DataFrame(data={'Country':i,
                      'Dates':col_tran,
                    'Recovered':data_points[0]})
    recovered_cases_frame=recovered_cases_frame.append(transformed_data)

recovered_cases_frame['Dates']=pd.to_datetime(recovered_cases_frame['Dates'],format='%m/%d/%y')
recovered_cases_frame['Dates']=recovered_cases_frame['Dates'].apply(lambda x:x.date())

print(' *** Transformation of recovered_cases data completed *** ')

###################################################################
# Transform Deaths Cases Data                                     #
###################################################################  

deaths_list=deaths_country_group['Country/Region'].unique()
col_tran=list(deaths_country_group)
col_tran.remove('Country/Region')

deaths_cases_frame=pd.DataFrame()
for i in  deaths_list:
    data_points=deaths_country_group[deaths_country_group['Country/Region']==i][col_tran].values
    transformed_data=pd.DataFrame(data={'Country':i,
                      'Dates':col_tran,
                    'Deaths':data_points[0]})
    deaths_cases_frame=deaths_cases_frame.append(transformed_data)

deaths_cases_frame['Dates']=pd.to_datetime(deaths_cases_frame['Dates'],format='%m/%d/%y')
deaths_cases_frame['Dates']=deaths_cases_frame['Dates'].apply(lambda x:x.date())

print(' *** Transformation of deaths_cases data completed *** ')

print(' *** Transformation of datasets completed *** ')

###################################################################
# Create Latest Data                                              #
################################################################### 

print(' *** Creating Files for latest data  *** ')
deaths_max_date=deaths_cases_frame[deaths_cases_frame['Dates']==deaths_cases_frame['Dates'].max()]
recovered_max_date=recovered_cases_frame[recovered_cases_frame['Dates']==recovered_cases_frame['Dates'].max()]
confirmed_max_date=confirmed_cases_frame[confirmed_cases_frame['Dates']==confirmed_cases_frame['Dates'].max()]

confirmed_max_date['Dates']=pd.to_datetime(confirmed_max_date['Dates'],format='%Y-%m-%d')

print(' *** Created Files for latest data  *** ')


###################################################################
# Create Latest minus 1 day Data                                  #
################################################################### 

print(' *** Creating Files for latest minus one data  *** ')

confirmed_cases_frame['Dates']=confirmed_cases_frame['Dates'].astype(str)
recovered_cases_frame['Dates']=recovered_cases_frame['Dates'].astype(str)
deaths_cases_frame['Dates']=deaths_cases_frame['Dates'].astype(str)

deaths_max_date_minus_one_day=deaths_cases_frame[deaths_cases_frame['Dates']==yesterday]
recovered_max_date_minus_one_day=recovered_cases_frame[recovered_cases_frame['Dates']==yesterday]
confirmed_max_date_minus_one_day=confirmed_cases_frame[confirmed_cases_frame['Dates']==yesterday]

print(' *** Shape of yesterday data ',confirmed_max_date_minus_one_day.shape)

print(' *** Created Files for latest data minus one day *** ')

###################################################################
# Set up Latitudes and Longitudes                                 #
###################################################################  

lat_lon_data.drop(columns=['Unnamed: 0'],inplace=True)
confirmed_max_date=confirmed_max_date.merge(lat_lon_data,on='Country')
print(' *** Set up of Latitude-Longitude file is Complete  *** ')

###################################################################
# Create Files used for Animation                                 #
###################################################################  

print(' *** Creating files for Animation  *** ')

deaths_cases_frame['Dates']=deaths_cases_frame['Dates'].astype(str)
confirmed_cases_frame['Dates']=confirmed_cases_frame['Dates'].astype(str)

deaths_cases_frame['key']=deaths_cases_frame['Dates']+deaths_cases_frame['Country']
confirmed_cases_frame['key']=confirmed_cases_frame['Dates']+confirmed_cases_frame['Country']

combined_frame=confirmed_cases_frame.merge(deaths_cases_frame,on='key')

combined_frame.drop(columns=['Dates_y','Country_y','key'],inplace=True)
combined_frame.rename(columns={'Country_x':'Country','Dates_x':'Dates'},inplace=True)

combined_frame_master=pd.DataFrame(columns=['Dates','Country','Confirmed','Deaths'])


for i in list(combined_frame['Country'].unique()):
    temp=combined_frame[combined_frame['Country']==i]
    temp['Dates']=pd.to_datetime(temp['Dates'])
    temp=temp.set_index('Dates')
    temp_resamp=temp.resample('D').interpolate()[::3].reset_index()
    combined_frame_master=combined_frame_master.append(temp_resamp,ignore_index=True)
    
combined_frame_master['Dates']=combined_frame_master['Dates'].astype(str)
combined_frame_master['Confirmed Cases (Scaled for purpose of graph)']=combined_frame_master['Confirmed'].apply(lambda x : np.arcsinh(x))
combined_frame_master.rename(columns={'Confirmed':'Confirmed Cases'},inplace=True)

print(' *** Completed set up of Animation files  *** ')

###################################################################
# Save Files                                                      #
################################################################### 
# Save Confirmed, Received and Death cases  (# Plots - 1,2,3 and 5 - Time line curves)

confirmed_cases_frame.to_csv('pre_processed_confirmed_cases.csv')
recovered_cases_frame.to_csv('pre_processed_recovered_cases.csv')
deaths_cases_frame.to_csv('pre_processed_deaths_cases.csv')

# Save Confirmed, Received and Death cases for Max date  (# Plot 4 and 6 - Map)

confirmed_max_date.to_csv('pre_processed_confirmed_max_date.csv')
recovered_max_date.to_csv('pre_processed_recovered_max_date.csv')
deaths_max_date.to_csv('pre_processed_deaths_max_date.csv')

# Save Confirmed, Received and Death cases for previous day 
confirmed_max_date_minus_one_day.to_csv('pre_processed_confirmed_max_date_minus_one_day.csv')
recovered_max_date_minus_one_day.to_csv('pre_processed_recovered_max_date_minus_one_day.csv')
deaths_max_date_minus_one_day.to_csv('pre_processed_deaths_max_date_minus_one_day.csv')


# Save files for Animated plot 
combined_frame_master.to_csv('pre_processed_combined_frame_master.csv')

print(' All the Files Saved. Program Ended Successfully *** ')

print('#'*60)
