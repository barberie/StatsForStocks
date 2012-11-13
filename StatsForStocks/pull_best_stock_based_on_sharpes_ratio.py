""" Construct a portfolio of equities that have high sharpe ratios
and low correlation to each other.  Script proceeds by:
    1. Reading data from every .csv file in the execution directory
    2. Calculating the sharpe ratios for each equity and sorting
    3. Taking the top _n_ equities according to sharpe ratio
    4. Computing a correlation matrix for those n equities
    5. Selecting a portfolio that minimizes the sum of cross-correlations
"""
import numpy as np
from numpy import recfromcsv
from itertools import combinations
import os
import datetime
import pandas
import operator
import math

class pull_best_stock_based_on_sharpes_ratio():

    
    def get_n_best(self):
        # Portfolio size is the number of instruments included in our 'best portfolio'
        portfolio_size=4

        # Stocks are sorted by sharpe ratio, then the top n stocks are analysed for cross-correlation
        top_n_equities=10

        # Get an array of file names in the current directory ending with csv
        path="C:/Users/Yogesh/Documents/Visual Studio 2010/Projects/PythonApplication3/PythonApplication3/stock_data/"
        index_file_name = 'C:/Users/Yogesh/Documents/Visual Studio 2010/Projects/PythonApplication3/PythonApplication3/stock_data/nifty.csv'
        files = [fi for fi in os.listdir('./stock_data/') if fi.endswith(".csv")]
        
        #Get an index file, which in out case will be the NSE NIFTY. This file will be used to obtain baseline for calculations like the Sorintino Ratio
        index_file = pandas.read_csv(index_file_name,index_col=0)

        #Get various values for nifty like ...daily return, average daily return, std deviation etc:
        #I am ignoring adj close and using close because the same has been used in all other stocks
        datalength_index = index_file['Close'].count()
        #First we start off by calculating the daily return of nifty
        index_file['Daily Return']=index_file['Close']
        for item in range(0 , datalength_index):
            if item == datalength_index-1:
                index_file['Daily Return'][item] = 0
            else:
                index_file['Daily Return'] = (index_file['Close'][item]/index_file['Close'][item+1])-1

        
        average_returns_index   = index_file['Daily Return'].mean()
        return_stdev_index      = index_file['Close'].std()
        sharpe_ratios_index     = math.sqrt(datalength_index)*average_returns_index/return_stdev_index

        # Grab a second array with just the names, for convenience.  These are used
        # to name columns of data.
        symbols = [os.path.splitext(fi)[0] for fi in files]

        #  This loops over every filename.  'i' is the index into the array, which we use to
        # add data to the other data structures we initialized.  That way the data for 'aapl' is
        # at the same index in every data structure.
        average_returns = []
        return_stdev = []
        sharpe_ratios = []
        sortino_ratio = []
        sortino_dict={}
        sharpes_sortinos_dict = {}
        #rtf = { 'Symbol' : pandas.Series(),\
        #        'Average Daily Returns' : pandas.Series(),\
        #        'Standard Deviation' : pandas.Series(),\
        #        'Sharpes' : pandas.Series(),\
        #        'Downside risk' : pandas.Series(),\
        #        'Average Excess Return' : pandas.Series(),\
        #        'Sortino' : pandas.Series()}
        #ratiosfile = pandas.DataFrame(rtf)
        #print ratiosfile
        
        all_symbols_file = 'all_symbols.csv'
        ratiosfile = pandas.read_csv(str(path)+str(all_symbols_file),index_col=0)
        ratiosfile['Symbol']=''
        ratiosfile['Average Daily Returns']=''
        ratiosfile['Standard Deviation']=''
        ratiosfile['Sharpes']=''
        ratiosfile['Downside risk']=''
        ratiosfile['Average Excess Return']=''
        ratiosfile['Sortino']=''
        for i, file in enumerate(files):
            #if 'ABAN' in files[i]:
            #    break
            test_flag=False
            files[i]=path+str(files[i])
            try:
                firstfile = pandas.read_csv(files[i],index_col=0)
            except:
                test_flag=True
                continue #???
            if test_flag:
                print ("AM I STILL HERE")
                print ("DAMN...WHATS THE PROBLEM")
            try:
                datalength = firstfile['Close Price'].count()
            except:
                print ("After the above checks I should not reach here.....but just checking")
                continue #???

            firstfile['Daily Return']=firstfile['Close Price']
            for item in range(0,datalength):
                if item == datalength-1:
                    firstfile['Daily Return'][item] = 0
                else:
                    firstfile['Daily Return'][item] = (firstfile['Close Price'][item]/firstfile['Close Price'][item+1])-1
            #****************************Calculating Sharpes Ratio*************
            # Initialize some arrays for storing data
            average_returns.append(firstfile['Daily Return'].mean())
            return_stdev.append(firstfile['Close Price'].std())
            sharpe_ratios.append(math.sqrt(datalength)*average_returns[-1]/return_stdev[-1])
            

            #****************************Calculating Sorintino Ratio*************
            firstfile['Excess Return'] = firstfile['Daily Return']
            firstfile['Negative Excess Return'] = firstfile['Daily Return']
            for n in range(0,datalength):
                firstfile['Excess Return'][n]=firstfile['Daily Return'][n]-average_returns_index
                firstfile['Negative Excess Return'][n]=firstfile['Excess Return'][n]
                
            
                if firstfile['Excess Return'][n] < 0:
                    firstfile['Negative Excess Return'][n] = firstfile['Excess Return'][n]
                else:
                    firstfile['Negative Excess Return'][n] = 0
            sumsq=0
            for n in range (0,datalength):
                sumsq = sumsq+math.pow(firstfile['Negative Excess Return'][n],2)
            downside_risk = math.sqrt(sumsq/datalength)
            average_excess_return = firstfile['Excess Return'].mean()
            sortino_ratio.append(average_excess_return/downside_risk)
            print ("symbol name")
            print symbols[i]

            sharpes_sortinos_dict[symbols[i]] =  [sharpe_ratios[-1],sortino_ratio[-1]]

            ratiosfile['Average Daily Returns'][i]=average_returns[-1]
            ratiosfile['Standard Deviation'][i]=return_stdev[-1]
            ratiosfile['Sharpes'][i]=sharpe_ratios[-1]
            ratiosfile['Downside risk'][i]=downside_risk
            ratiosfile['Average Excess Return'][i]=average_excess_return
            ratiosfile['Sortino'][i]=sortino_ratio[-1]
            ratiosfile['Symbol'][i]=symbols[i]
        
            
            
            #firstfile.to_csv(str(path) + str (symbols[i]) +str(ratio_file) + '.csv')
        
        ratio_file = 'ratio_file'
        list_of_ratios = pandas.DataFrame(ratiosfile, columns=['Symbol','Average Daily Returns','Standard Deviation','Sharpes','Downside risk','Average Excess Return','Sortino'])
        list_of_ratios.sort(['Sortino','Sharpes'],ascending=False,inplace=True)
        #list_of_ratios.to_csv('C:/Users/Yogesh/Documents/Visual Studio 2010/Projects/PythonApplication3/PythonApplication3/stock_data/nifty_ratios.csv')
        return list_of_ratios
    
    def __init__(self):
        print ("Initiating calculation of best sharpes ratio")
        #print self.get_n_best()

#tester = pull_best_stock_based_on_sharpes_ratio()
if __name__ == "__main__":
    calculator = pull_best_stock_based_on_sharpes_ratio()
    print calculator.get_n_best()

