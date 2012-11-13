import urllib
import urllib2
import mechanize
import cookielib
import datetime
import sys
import os
import time
from html2csv import *
import pandas
import pull_best_stock_based_on_sharpes_ratio


#
# TBD
# Add (a lot more) TBDs where needed
# REMOVE THE FILTHY HARDCODED pathnames
# ADD DOC STRINGS and comments 
# Add debug/test/production code
# Few TBDs are mentioned in random places....Add a pointer to all of them
# Add testing results for network and csv convesrion 
# Add test cases (DO NOT FORGET TDD)
#   Add lettuce tests
# Where the hell are classes??? reorganize and Refactor
# Test on different environments 
# Add a list of dependencies
#



#The url to the service we need
URL = "http://www.nesindia.com"

def get_data(data_path):

    #Create path if it doesn't exist
    if not (os.access(data_path, os.F_OK)):
        os.makedirs(data_path)

    _now =datetime.datetime.now();
    miss_ctr=0; #Counts how many symbols we could not get

    #Get one time data from initial setup of nseindia.com connection
    b,cj,response=setup_initial_nse_connection()
    returned_sorted_stock_list=[]

    res = get_file_with_all_script_names(b,cj,response)
    file_name='all_symbols.csv'
    write_to_file(res,data_path,file_name)

    ls_symbols_df=pandas.read_csv(str(data_path)+str(file_name))
    #
    # Even though we are not using this now, we can generate the script names as used by Yahoo Finance and 
    # use them for further data collection.
    # TBD: Write a test to perform data collection using both nseindoa.com and yahoo finance and compare the results
    # This will give us a drection for performance improvement, or in order to transfer gathering data to yahoo finance.
    # I would prefer data collection from Yahoo Finance, because it likes (or atleast helps) automated scripts to do this job.
    # nseindia.com DOES NOT like automated scripts and puts a lot of hinderence in the way of data collection.
    # However my contention is that when this script is expanded to gather real time data, nseindia.com would be a better option 
    # in terms of sheer performance.
    #
    #ls_symbols_df['Yahoo_Symbol']=''
    #for item in range(0,ls_symbols_df['SYMBOL'].count()):
    #    ls_symbols_df['Yahoo_Symbol'][item] = (ls_symbols_df['SYMBOL'])[item][0:9]+'.NS'
    #print ls_symbols_df['Yahoo_Symbol'].to_string()
    
    ls_symbols=ls_symbols_df['SYMBOL']
    
    res = get_the_nifty_file_for_base_standards(b,cj,response)
    file_name='nifty.csv'
    write_to_file(res,data_path,file_name)
    
    for symbol in ls_symbols:
        symbol_name = symbol

        symbol_data=list()
        params= urllib.urlencode ({'fromDate':'01-Jan-1971', 'toDate':'13-Nov-2012', 'datePeriod':'unselected', 'hidddDwnld':'true', 'symbol': str(symbol)})
        
        #For each symbol, get the data in res and save it to file wth same name as symbol
        res = get_data_from_params_and_symbol(params,symbol_data,b,cj,response)
        file_name=str(symbol_name)+'.html'
        write_to_file(res,data_path,file_name)
        
        #Convert HTML file to CSV file
        #Decide weather to do this outside the for loop after gathering all the data
        # This will speed up gathering data on high speed networks, but conversion time on low speed networks is negligible
        # I have seen the effects of this dragging on a high speed network (more than 10MBps). (Results and graphs to be posted)
        # Fortunately, 99% of time, I am on a super-slow network and so this processing tome is negligible in my case
        # TBD - Add a speed test and put this in the right place
        convert_html2csv(data_path, symbol_name)


    #Once data is converted we can play around with various ratios and calculations for computational investing in general
    #Here I will start with 3 things:
    #1. average daily earnings
    #2. standard deviation
    #3. The above 2 are mainly to get to this metric - Sharpe's Ratio
    # Based on this we will collect 10 stocks based on highest sharpes ratio and sortinos ratio
    returned_sorted_stock_list = calculate_sharpes_and_sortinos_ratio()
    #print returned_sorted_stock_list.to_string()
    file_name='sortino_and_sharpes_ratio_of_all_stocks'
    returned_sorted_stock_list.to_csv(str(data_path+file_name))

def write_to_file(file_data,data_path,file_name):
    #Get file handler        
    file_handler=open(str(data_path)+str(file_name), 'w+')
    #Writing the response
    file_handler.write(file_data.read())
    #Close the file
    file_handler.close()


def calculate_sharpes_and_sortinos_ratio():
    #tester = []
    tester = pull_best_stock_based_on_sharpes_ratio.pull_best_stock_based_on_sharpes_ratio().get_n_best()
    return tester



def convert_html2csv(data_path, symbol_name):
        f= open (data_path + symbol_name + ".html", 'r')
        f2= open (data_path + symbol_name + ".csv", 'w')
        parser = html2csv()
        parser.feed( f.read() )
        f2.write( parser.getCSV() )
        f.close()
        f2.close()

    
def setup_initial_nse_connection():
    #Create a browser instance
    b=mechanize.Browser()

    #Dont allow Robots.txt to fail us:
    cj = cookielib.MozillaCookieJar()
    b.set_cookiejar(cj)
    b.set_handle_robots(False)
    b.set_handle_equiv(False)
    b.set_handle_gzip(True)
    b.set_handle_redirect(True)
    b.set_handle_referer(True)
    
    # Follows refresh 0 but not hangs on refresh > 0
    b.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    
    # Want debugging messages?
    #b.set_debug_http(True)
    #b.set_debug_redirects(True)
    #b.set_debug_responses(True)
    
    
    
    #This is cheating -- ok?
    b.addheaders= [("User-agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")]
    #Load the page
    response = b.open(URL)
    return b,cj,response

def get_file_with_all_script_names(b,cj,response):
    URL="http://nseindia.com/content/equities/EQUITY_L.csv"
    req = mechanize.Request(URL)
    req.add_header('Referer', response)
    req.add_header('Accept', ' application/json, text/javascript, */*')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    req.add_header('X-Requested-With', 'XMLHttpRequest')
    cj.add_cookie_header(req)
    res = b.open(req)
    return res

def get_the_nifty_file_for_base_standards(b,cj,response):
    #today = datetime.date.today()
    #params= urllib.urlencode ({'underlying':'NIFTY', 'instrument': 'FUTIDX', 'expiry': str(str(today.day)+str(today.month)+str(today.year)), 'type' : 'SELECT', 'strike' : 'SELECT','fromDate':'01-Jan-2011', 'toDate':'31-Dec-2011', 'datePeriod':'unselected', 'fileDnld' : 'undefined'})
    #URLeg="http://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuoteFO.jsp?underlying=NIFTY&instrument=FUTIDX&type=-&strike=-&expiry=29NOV2012"
    #URL="http://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/getFOHistoricalData.jsp?%s" % params
    #req = mechanize.Request(URL)
    #req.add_header('Referer', response)
    #req.add_header('Accept', ' application/json, text/javascript, */*')
    #req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    #req.add_header('X-Requested-With', 'XMLHttpRequest')
    #cj.add_cookie_header(req)
    #res = b.open(req)
    #return res

    #For the loive of GOD - NSE REALLY hates pulling data 
    #I have observed that nseindia.com does not maintain proper long term data
    # of the futures index nifty. Most of the trading days the data is missing.
    #Therefore, Its best if we pull this data from yahoo finance 
    params= urllib.urlencode ({'a':0, 'b':1, 'c':1971, 'd':11, 'e':13, 'f':2012, 'g':'d', 'ignore':'.csv', 's': '^NSEI'})
    print ("http://ichart.finance.yahoo.com/table.csv?%s" % params)
    url_get= urllib2.urlopen("http://ichart.finance.yahoo.com/table.csv?%s" % params)
    return url_get

        

def get_data_from_params_and_symbol(params,symbol_data,b,cj,response):
        #print("*"*50)
        URL = "http://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/getHistoricalData.jsp?%s" % params
        #print URL2
    
        
        #Loading URL2 without setting proper response will cause the request to fail. So we need to open nseindia.com before getting the quotes directly
        req = mechanize.Request(URL)
        req.add_header('Referer', response)
        req.add_header('Accept', ' application/json, text/javascript, */*')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
        req.add_header('X-Requested-With', 'XMLHttpRequest')
        cj.add_cookie_header(req)
        res = b.open(req)
        return res

        



def main():
    
    path = './stock_data/'
    get_data(path)

if __name__ == '__main__':
    main()