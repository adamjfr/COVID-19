# Import Statements

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from operator import itemgetter
from matplotlib.pyplot import figure
import matplotlib as mpl
mpl.rcParams['lines.linewidth'] = 3


# Load Data

df = pd.read_csv('state_daily.csv', parse_dates=['date'])
df_us = pd.read_csv('us_daily.csv', parse_dates=['date'])
state_pops = pd.read_csv('state_pops.csv', header=None).set_index(2)


# Drop Deprecated Variables

df = df.drop(['checkTimeEt','commercialScore','dateChecked','dateModified',
              'deathIncrease','grade','hospitalized','hospitalizedIncrease',
              'negativeIncrease','negativeRegularScore','negativeScore',
              'posNeg','positiveIncrease','positiveScore','score','total',
              'totalTestResultsIncrease'],axis=1)

# Create Dictionary of DataFrames, One for Each State

states = df.state.unique()

dfs = {}

dfs['USA'] = df_us.set_index('date')

for state in states:
    key = state
    value = df[df.state==state].set_index('date').drop('state', axis=1)
    dfs[key] = value




# VARIABLE CONSTRUCTION

# Daily and Cumulative Variables

for state in dfs.keys():
    # New Positives
    dfs[state]['new_pos'] = dfs[state]['positive'] - dfs[state]['positive'].shift(-1)

    # New Negatives
    dfs[state]['new_neg'] = dfs[state]['negative'] - dfs[state]['negative'].shift(-1)

    # New Tests Total
    dfs[state]['new_tests'] = dfs[state]['new_pos'] + dfs[state]['new_neg']

    # Daily percent positive
    dfs[state]['daily_pct_pos'] = 100 * dfs[state]['new_pos'] / dfs[state]['new_tests']

    # Total Tests to Date
    dfs[state]['total_tests'] = dfs[state]['positive'] + dfs[state]['negative']

    # New Hospitalizations
    dfs[state]['new_hosp'] = dfs[state]['hospitalizedCumulative'] - dfs[state]['hospitalizedCumulative'].shift(-1)

    # New Deaths
    dfs[state]['new_deaths'] = dfs[state]['death'] - dfs[state]['death'].shift(-1)

    # max(New Positives)
    dfs[state]['peak_rate'] = np.max(dfs[state]['new_pos'])

    # Date of max(New Positives)
    dfs[state]['peak_date'] = dfs[state].index[dfs[state]['new_pos'] == dfs[state]['peak_rate']][0]

    # Active cases
    dfs[state]['active'] = dfs[state]['positive'] - dfs[state]['death'] - dfs[state]['recovered']

    # Daily growth factor relative to positive tests
    dfs[state]['daily_growth_factor_a'] = dfs[state]['new_pos'] / dfs[state]['positive']

    # Daily growth factor relative to ('Active' = pos-deaths-recovered)
    dfs[state]['daily_growth_factor_b'] = dfs[state]['new_pos'] / dfs[state]['active']

# PER CAPITA Daily and Cumulative Variables

for state in dfs.keys():
    # New Positives
    dfs[state]['new_pos_pc'] = dfs[state]['new_pos'] / state_pops.loc[state][1]

    # New Negatives
    dfs[state]['new_neg_pc'] = dfs[state]['new_neg'] / state_pops.loc[state][1]

    # New Tests Total
    dfs[state]['new_tests_pc'] = dfs[state]['new_tests'] / state_pops.loc[state][1]

    # Total Tests to Date
    dfs[state]['total_tests_pc'] = dfs[state]['total_tests'] / state_pops.loc[state][1]

    # New Hospitalizations
    dfs[state]['new_hosp_pc'] = dfs[state]['new_hosp'] / state_pops.loc[state][1]

    # New Deaths
    dfs[state]['new_deaths_pc'] = dfs[state]['new_deaths'] / state_pops.loc[state][1]

    # Active cases
    dfs[state]['active'] = dfs[state]['positive'] - dfs[state]['death'] - dfs[state]['recovered']


######################################################
######################################################

# Set size of rolling window
window = 3

######################################################
######################################################


# Rolling Average Variables

for state in dfs.keys():
    # ROLLING AVERAGES OF:

    # new cases
    dfs[state]['new_cases_rolling'] = dfs[state]['new_pos'].rolling(window=window).mean()

    # hospitalizations
    dfs[state]['new_hosp_rolling'] = dfs[state]['new_hosp'].rolling(window=window).mean()

    # new deaths
    dfs[state]['new_deaths_rolling'] = dfs[state]['new_deaths'].rolling(window=window).mean()

    # daily percent positive tests
    dfs[state]['daily_pct_pos_rolling'] = 100 * (dfs[state]['new_pos'] / dfs[state]['new_tests']).rolling(
        window=window).mean()

# PER CAPITA Rolling Average Variables

for state in dfs.keys():
    # Rolling averages of new cases, new hospitalizations, new deaths

    dfs[state]['new_cases_rolling_pc'] = dfs[state]['new_pos'].rolling(window=window).mean() / state_pops.loc[state][1]
    dfs[state]['new_hosp_rolling_pc'] = dfs[state]['new_hosp'].rolling(window=window).mean() / state_pops.loc[state][1]
    dfs[state]['new_deaths_rolling_pc'] = dfs[state]['new_deaths'].rolling(window=window).mean() / \
                                          state_pops.loc[state][1]