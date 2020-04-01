# Import Libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import datetime as dt
import re
import os

# Define Constants
url_qualifier='https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series/'
file_qualifier_confirmed='Time_Series_Confirmed'
file_qualifier_deaths='Time_Series_Deaths'
file_qualifier_recovered='Time_Series_Recovered'
confirmed_file='time_series_covid19_confirmed_global'
deaths='time_series_covid19_deaths_global'
recovered='time_series_covid19_recovered_global'
extension='.csv'
file_list=[confirmed_file,deaths,recovered]



# Define helper methods
def get_url_data(date_val):
    start=dt.datetime.now()
    url = url_qualifier + date_val + extension
    
    response = requests.get(url)
    if str(response)=='<Response [200]>':
          soup= BeautifulSoup(response.text, 'html.parser')
    else:
          print('get_url failed. Bad response received : {}'.format(str(response)))
    print('Total Execution Time {}'.format(dt.datetime.now()-start))
    return soup    

def extract_headers(soup_data):
    html_text=soup_data.findAll('tr')
    listed_html_text=list(html_text)
    print('Length of listed html text: {}'.format(len(listed_html_text)))
    cols=[]
    b=list(listed_html_text[0])
    for i in range(0,len(b)):
        if str(b[i])!= '\n':
            node=re.match("<td class=*",str(b[i]))
            if not node:
                value=re.match('<th>(.*)</th>',str(b[i])).group(1)
                cols.append(value)
    return cols

def extract_data(soup_data):
    data_array=[]
    html_text=soup_data.findAll('tr')
    listed_html_text=list(html_text)
    for j in range(1,len(listed_html_text)):
        b=list(listed_html_text[j])
        d=[]
        for i in range(0,len(b)):
            if str(b[i])!= '\n':
                node=re.match("<td class=*",str(b[i]))
                if not node:
                    value=re.match('<td>(.*)</td>',str(b[i])).group(1)
                    d.append(value)
        data_array.append(d)
    return data_array

print('Current working Directory : ' + os.getcwd())

# Define Main method
if __name__ == "__main__":

    for k in file_list:  
        print('Data extraction started for {}'.format(k))   
        soup=get_url_data(k)
        cols=extract_headers(soup)
        data_array=extract_data(soup)
        data = pd.DataFrame(data_array, columns=cols)
        filename=k+extension
        data.to_csv(filename,encoding='utf-8',index=False)
        print('Data extraction complete for Date {}. Shape of data {}.'.format(k,data.shape))
        time.sleep(40) 