#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests as req
from json import loads
import datetime
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import cufflinks as cf


# In[2]:


def setBase():
    '''
    Function for setting the base currency
    '''

    while True:
        print('Please enter the currency you wish to use as the base currency in the form of a three character string (i.e. EUR, JPY, USD)')

        base = input('Input base currency - ').upper()

        if len(base) > 3:
            print("That's too long! Please enter a three character string and try again!")
        elif len(base) < 3:
            print("That's too short! Please enter a three character string and try again!")
        elif len(base) == 3:
            print(f"You have selected - {base}")
            return base


# In[3]:


def setCurrencyCompare():
    '''
    Function for setting the currencies to compare against
    '''

    while True:
        print('Please enter the currency you wish to compare against in the form of a three character string (i.e. EUR, JPY, USD)')
        print('You can enter multiple currencies using a comma after the first currency (i.e. JPY,GBP,USD)')
        print('Or you can leave this blank and hit enter to return ALL currencies')

        currency = input('Input currency - ').upper()

        return currency


# In[4]:


def fetchRates():
    '''
    Function for deciding which rates to fetch from the API
    '''

    while True:
        print('Please enter which rates you would like to fetch')
        print('2 - historical rates (set date)')
        print('3 - historical rates (time period between two dates)')
        print('5 - return to main menu')

        while True:
            try:
                choice = int(input('Enter your choice - '))
                break
            except:
                print("That's not a number - please try again!")

        if choice == 2:
            historicalRatesSet()
        elif choice == 3:
            historicalRatesPeriod()
        elif choice == 5:
            print('Returning to main menu')
            break
        else:
            print(f'{choice} is invalid, please try again!')


# In[5]:


def historicalRatesSet():
    '''
    Function for getting historical rates from the API (on a set date)
    '''
    while True:
        try:
            print('NOTE: The furthest you can go back to is 2018!')

            year = setYear()
            
            month = setMonth()

            day = setDay()
            break
        except ValueError:
            print('Incorrect value detected! Please try again!')
    
    baseCurrency = setBase()
    compareCurrency = setCurrencyCompare()

    currencyList = []
    valueList = []
    historicalDate = f'{day}-{month}-{year}'

    try:
        print(f'Now fetching exchange rates for {baseCurrency} on the following date: {day}-{month}-{year}')
        #Get data
        response = req.get(url=f'https://api.exchangeratesapi.io/{year}-{month}-{day}?base={baseCurrency}&symbols={compareCurrency}&symbols=JPY,USD,CAD,GBP,NZD,INR')
        #Deserialise response into Python dictionary
        responseDict = loads(response.text)
        #the response has multiple dictionaries
        exchangeDict = responseDict['rates']
        print('Complete!')
        print(f'Exchange rate for {baseCurrency} on {day}-{month}-{year}')
        for key,value in exchangeDict.items():
            currencyList.append(key)
            valueList.append(f'{value:.2f}')

        completeDict = {'Currency':currencyList, 'Exchange':valueList}
        #make a dataframe
        df = pd.DataFrame(completeDict)
        df = df.sort_values(by='Currency')
        print(df)
        print('Printing results to CSV file...')
        df.to_csv(f'historical-{historicalDate}-{baseCurrency}.csv',index=False)
        print(f'CSV created! Written to {os.getcwd()}')
        print(f'File is called - historical-{historicalDate}-{baseCurrency}')
        print('Now creating table - please wait...')
        fig = go.Figure(data=[go.Table(
    header=dict(values=list(df.columns),),
    cells=dict(values=[df.Currency, df.Exchange]))])
        fig.show()
        fig.write_html(f'historical-{historicalDate}-{baseCurrency}.html')
        print(f'Table has been saved as a HTML file called - historical-{historicalDate}-{baseCurrency}')
    except:
        print('An error has occurred - please try again!')


# In[7]:


def historicalRatesPeriod():
    '''
    Function for getting historical rates from the API (on a time period)
    '''

    while True:
        try:
            print('NOTE: Creating start date')
            print('NOTE: The furthest you can go back to is 1999!')

            year = setYear()
            
            month = setMonth()

            day = setDay()

            startDate = f'{year}-{month}-{day}'
            break
        except ValueError:
            print('Incorrect value detected! Please try again!')
    
    while True:
        try:
            print('NOTE: Creating end date')
            print('NOTE: The furthest you can go back to is 1999!')

            year = setYear()
            
            month = setMonth()

            day = setDay()

            endDate = f'{year}-{month}-{day}'
            break
        except ValueError:
            print('Incorrect value detected! Please try again!')
    
    baseCurrency = setBase()
    compareCurrency = setCurrencyCompare()

    try:
        print(f'Now fetching exchange rates for {baseCurrency} between the following dates: {startDate} - {endDate}')
        #Get data
        response = req.get(url=f'https://api.exchangeratesapi.io/history?start_at={startDate}&end_at={endDate}&base={baseCurrency}&symbols={compareCurrency}&symbols=JPY,USD,CAD,GBP,NZD,INR')
        #Deserialise response into Python dictionary
        responseDict = loads(response.text)
        #the response has multiple dictionaries
        exchangeDict = responseDict['rates']
        print('Complete!')
    
        #build DataFrame and clean up
        df = pd.DataFrame(exchangeDict)
        df = df.round(decimals=2)
        df = df.reindex(sorted(df.columns), axis=1)
        df = df.reindex(sorted(df.index), axis=0)
        df = df.rename_axis("Dates", axis="columns")
        df = df.rename_axis("Currency Code", axis="rows")
        print(df)
        print('Printing results to CSV file...')
        df.to_csv(f'historical-{startDate}-{endDate}-{baseCurrency}.csv',index=True)
        print(f'CSV created! Written to {os.getcwd()}')
        print(f'File is called - historical-{startDate}-{endDate}-{baseCurrency}')

        while True:
            print('Do you want to print the mean (average) of each currency to a seperate CSV file?')
            print("Type 'Y' for yes or 'N' for no")
            meanChoice = input('Enter your choice - ').upper()
            if meanChoice == 'Y':
                df.mean(axis=1).to_csv(f'historical-{startDate}-{endDate}-{baseCurrency}-Mean.csv',index=True)
                break
            elif meanChoice == 'N':
                print('Not printing the mean of currencies')
                break
            else:
                print(f'{meanChoice} - is invalid, please try again!')

        #build scatter graph and customise it
        print('Now creating scatter plot - please wait...')
        fig = px.scatter(data_frame=df, title=f'Historical rates between {startDate} - {endDate} for {baseCurrency}')
        fig.update_traces(marker=dict(size=15,line=dict(width=2,color='DarkSlateGrey')))
        fig.show()
        fig.write_html(f'historical-{startDate}-{endDate}-{baseCurrency}.html')
        print(f'Scatter plot has been saved as a HTML file called - historical-{startDate}-{endDate}-{baseCurrency}')
    except:
        print('An error has occurred - please try again!')

def setYear():
    '''
    Function for setting the year from user
    '''
    while True:
        try:
            print('Please enter the year (as a numerical value)')
            year = int(input('Enter the year - '))

            if year < 2018:
                print('Please enter a valid year!')
            else:
                return year
        except ValueError:
            print('Incorrect value detected! Please try again!')

def setMonth():
    '''
    Function for setting the month from user
    '''
    while True:
        try:
            print('Please enter the month (as a numerical value)')
            month = int(input('Enter the month - '))

            if month < 1 or month > 12:
                print('Please enter a valid month!')
            else:
                return month
        except ValueError:
            print('Incorrect value detected! Please try again!')

def setDay():
    '''
    Function for setting the day from user
    '''
    while True:
        try:
            print('Please enter the day (as a numerical value)')
            day = int(input('Enter the day - '))

            if day < 1 or day > 31:
                print('Please enter a valid day!')
            else:
                return day
        except ValueError:
            print('Incorrect value detected! Please try again!')

def main():
    '''
    The main function for running the program
    '''

    while True:
        print('Welcome to the Currency Exchange Program!')
        print('Enter the character inbetween the parentheses')

        print('(F)etch rates')
        print('(A)bout')
        print('(Q)uit')


        choice = input('Enter your choice - ').upper()

        if choice == 'F':
            fetchRates()
        elif choice == 'A':
            print(
                '''
The currency exchange program uses the foreign exchange rates
                ''')
        elif choice == 'Q':
            print('Goodbye!')
            break
        else:
            print(f"{choice} is invalid! Please try again!")

main()


# In[ ]:




