
import pandas as pd
from datetime import datetime as dt
import statsmodels.api as sm
import numpy as np
import statistics

df = pd.read_csv('CRSP.csv')

conditional = df['SHRCD']<13



def IHateItHere(eststartdate,estenddate,regstartdate,regenddate,period):
    USCommondf = df[conditional].copy()

    USCommondf.loc[:, 'date'] = pd.to_datetime(USCommondf['date'])
    USCommondf.loc[:,'MCAP'] = USCommondf['PRC'] * USCommondf['SHROUT']
# Sort the DataFrame by 'Permno' and 'Date'
    USCommondf.sort_values(by=['PERMNO', 'date'], inplace=True)

# Group by 'Permno' and shift the 'RET' column up by one date
    USCommondf['NextRet'] = USCommondf.groupby('PERMNO')['RET'].shift(-1)
    USCommondf['NextMRet'] = USCommondf.groupby('PERMNO')['vwretd'].shift(-1)

    start_date = pd.to_datetime(eststartdate)
    end_date = pd.to_datetime(estenddate)

    # Filter for the years 1973 to 1975.
    beta75filtdf = USCommondf[(USCommondf['date'] >= start_date) & (USCommondf['date'] <= end_date)]

    # Group by 'PERMNO' and filter out groups with fewer than 36 observations.
    grouped_df = beta75filtdf.groupby('PERMNO').filter(lambda group: len(group) >= 36)

    # Calculate the total 'MCAP' for each 'PERMNO.'
    permno_mcap_totals = grouped_df.groupby('PERMNO')['MCAP'].sum().reset_index()

    # Sort by total 'MCAP' in descending order and get the top 500 'PERMNO's.
    top_500_permnos = permno_mcap_totals.sort_values(by='MCAP', ascending=False).head(500)

    # 'top_500_permnos' now contains the 500 largest 'PERMNO's by 'MCAP' for the specified years and filter conditions.
    # Filter 'USCommondf' for the specified date range.
    filtered_75_df = USCommondf[(USCommondf['date'] >= start_date) & (USCommondf['date'] <= end_date)]

    # Filter 'filtered_75_df' by the 'PERMNO's in 'top_500_permnos'.
    filtered_75_df = filtered_75_df[filtered_75_df['PERMNO'].isin(top_500_permnos['PERMNO'])]

    # Sort the filtered DataFrame by 'PERMNO' and 'date' to ensure data is in the correct order for calculations.
    filtered_75_df = filtered_75_df.sort_values(['PERMNO', 'date'])

    # Calculate 'PRC' returns from one period to the next.
    filtered_75_df['prc_return'] = filtered_75_df.groupby('PERMNO')['PRC'].pct_change()

    # Create an empty DataFrame to store the beta values.
    beta_list = []

    # Perform the regression for each 'PERMNO' to calculate the beta.
    for permno, group in filtered_75_df.groupby('PERMNO'):
        X = group['vwretd']
        y = group['prc_return']
    
        model = sm.OLS(y, X, missing='drop').fit()
        beta = model.params['vwretd']
    
        beta_list.append({'PERMNO': permno, 'Beta': beta})

# Create the 'beta_75_df' DataFrame from the list of dictionaries.
    beta_75_df = pd.DataFrame(beta_list)


    # Assuming 'beta_75_df' is your DataFrame with columns 'PERMNO' and 'Beta'.

    # Sort 'beta_75_df' by 'Beta' values.
    beta_75_df_sorted = beta_75_df.sort_values(by='Beta')

    # Define the number of portfolios or DataFrame splits.
    num_portfolios = 10
    portfolio_size = len(beta_75_df_sorted) // num_portfolios

    # Create a list of DataFrames to store the separate portfolios.
    portfolio_dataframes = []

    # Split the sorted DataFrame into ten different portfolios.
    for i in range(num_portfolios):
        start_idx = i * portfolio_size
        end_idx = start_idx + portfolio_size

        # Check for the last portfolio to include the remaining rows.
        if i == num_portfolios - 1:
            portfolio = beta_75_df_sorted.iloc[start_idx:]
        else:
            portfolio = beta_75_df_sorted.iloc[start_idx:end_idx]

        portfolio_dataframes.append(portfolio)

    # The 'portfolio_dataframes' list now contains ten DataFrames, each representing a different portfolio based on beta values.
    
    start_date = pd.to_datetime(regstartdate)
    end_date = pd.to_datetime(regenddate)

    USCommon76testdf = USCommondf[(USCommondf['date'] >= start_date) & (USCommondf['date'] <= end_date)]

    unique_dates = USCommon76testdf['date'].unique().tolist()

    beta = []
    count = 1
    for permnos in portfolio_dataframes:
        # Filtering USCommondf based on PERMNOs in Permnos
        filtered_USCommondf = USCommondf[USCommondf['PERMNO'].isin(permnos['PERMNO'])]
        X = []
        y = []
        for day in unique_dates:
            dayfilter = filtered_USCommondf[filtered_USCommondf['date'] == day].copy()
            total_for_day = dayfilter['MCAP'].sum()
            dayfilter['Weight'] = dayfilter['MCAP'] / total_for_day
            dayfilter['NextRet'] = pd.to_numeric(dayfilter['NextRet'], errors='coerce')
            dayfilter['Wreturn'] = dayfilter['Weight']*dayfilter['NextRet']
            first = dayfilter['NextMRet'].iloc[0]
            X.append(dayfilter['Wreturn'].sum())
            y.append(first)
        returnlist = [m+1 for m in X]
        portfolioret = np.prod(returnlist)-1

        holdReturn = statistics.mean(X)
        model = sm.OLS(y, X, missing='drop').fit()
        beta.append((period,count,model.params,holdReturn,portfolioret))
        count += 1
    return(beta)

startyear = 1973

datelist = []

yearcount = 0
while yearcount < 8:
    startcalyear = startyear + yearcount*5
    endcalyear = startyear + 2 +yearcount*5
    startregyear = startyear + 3+ yearcount*5
    endregyear = startyear + 7 + yearcount*5
    yearcount += 1
    startcalyearstring = str(startcalyear) 
    endcalyearstring =  str(endcalyear)
    startregyearstring = str(startregyear)
    endregyearstring =  str(endregyear)
    datelist.append((startcalyearstring+'-01-01',endcalyearstring+'-12-31',startregyearstring+'-01-01',endregyearstring+'-12-31',yearcount))

allthebetas = []
whilecounter = 0
while whilecounter < 8:
    allthebetas = allthebetas+IHateItHere(*datelist[whilecounter])
    print(len(allthebetas))
    print(allthebetas)
    whilecounter += 1


print(len(allthebetas))
print(allthebetas)
fixedtuples = [(a,b,c[0],d,e) for (a,b,c,d,e) in allthebetas]

print(fixedtuples)
bigdf = pd.DataFrame(fixedtuples, columns=['period','decile','beta','arithmeanret','BAHR'])

print(bigdf.head())

bigdf.to_csv('yeah.csv')