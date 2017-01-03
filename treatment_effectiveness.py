import pandas as pd
import numpy as np
from scipy.stats.stats import pearsonr
from scipy.stats import ttest_ind
import math
import datetime

PERIODICITY_THRESHOLD = 0.75 #how periodic a treatment seems to be before its considered recurring
TIMEFRAMES = [0, 1, 2, 7] #all of the timeframes (in days) over which we compare symptom severity for sporatic tags

#Attempts to determine if a treatment is periodic
#We want to know this as there are two different ways that a treatment could be considered effective
#If a treatment is taken on a regular basis, then we want to know if the user's symptoms have decreased during the timeframe that they've taken the treatment
#If a treatment only happens occasionally (good sleep for example), then we want to know how how this has affected the user's symptoms within certain ranges of the event
#There are a lot of ways to measure periodicity.  Most standard takes the Fourier transform.
#At least for now, going with the more simple and interpretable method of taking the percentage of days that the user logged the trackable, as this takes into account
#the fact that most users log sporatically
def isTreatmentPeriodic(user_df, treatment_name):
    treatment_df = user_df[(user_df['trackable_name'] == treatment_name)]
    treatment_start_date = treatment_df['checkin_date'].min()
    treatment_end_date = treatment_df['checkin_date'].max()
    treatment_range = user_df[(user_df['checkin_date'] > treatment_start_date) & (user_df['checkin_date'] < treatment_end_date)]
    percent_logged = float(len(set(treatment_range['checkin_date']))) / float(len(set(user_df['checkin_date'])))
    print treatment_name + " " + str(percent_logged)
    return percent_logged > PERIODICITY_THRESHOLD

#Determines if a treatment affects a symptom over a significant period of time, this method only works for treatments that are used regularily
#Turns the duration of treatment into a window, and measures the severity of symptoms inside and outside of that window
#See notebook for more details of how this method was arrived at
def effectivenessInWindow(user_df, treatment_name, symptom_name):
    treatment_df = user_df[(user_df['trackable_name'] == treatment_name)]
    treatment_start_date = treatment_df['checkin_date'].min()
    treatment_end_date = treatment_df['checkin_date'].max()
    treatment_range = user_df[(user_df['checkin_date'] >= treatment_start_date) & (user_df['checkin_date'] <= treatment_end_date)]
    no_treatment_range = user_df[(user_df['checkin_date'] < treatment_start_date) | (user_df['checkin_date'] > treatment_end_date)]

    #create lists of trackable_values inside the treatment dates, outside treatment dates, and for all dates
    treatment_values = pd.to_numeric(treatment_range[treatment_range['trackable_name'] == symptom_name]['trackable_value']).values
    no_treatment_values = pd.to_numeric(no_treatment_range[no_treatment_range['trackable_name'] == symptom_name]['trackable_value']).values
    population_values = pd.to_numeric(user_df[user_df['trackable_name'] == symptom_name]['trackable_value']).values

    #remove nans
    treatment_values = [x for x in treatment_values if (math.isnan(x) == False)]
    no_treatment_values = [x for x in no_treatment_values if (math.isnan(x) == False)]
    population_values = [x for x in population_values if (math.isnan(x) == False)]

    effectiveness = np.mean(no_treatment_values) - np.mean(treatment_values)
    tstat, pvalue = ttest_ind(treatment_values, population_values)  #best method I could think of to determine the significance of the difference of means
    return effectiveness, pvalue

#Get a measure of the correlation between days with a treatment versus not, with a specified timedelta
def effectivenessAtTime(user_df, treatment_name, symptom_name, timeframe):
    treatment_df = user_df[(user_df['trackable_name'] == treatment_name)]
    treatment_dates = treatment_df['checkin_date'].apply(lambda x: x + datetime.timedelta(days=timeframe))
    treatment_range = user_df[(user_df['checkin_date'].isin(treatment_dates)) & (user_df['trackable_name'] == symptom_name)]

    #if there aren't any days that the symptom is logged, return 0 with 0 certainty
    if len(treatment_range) == 0:
        return 0,0

    treatment_values = pd.to_numeric(treatment_range['trackable_value']).values
    population_values = pd.to_numeric(user_df[user_df['trackable_name'] == symptom_name]['trackable_value']).values

    # remove nans
    treatment_values = [x for x in treatment_values if (math.isnan(x) == False)]
    population_values = [x for x in population_values if (math.isnan(x) == False)]

    effectiveness = np.mean(population_values) - np.mean(treatment_values)
    tstat, pvalue = ttest_ind(treatment_values, population_values)
    return effectiveness, pvalue

def getEffectiveness(user_df,treatment_name,symptom_name):
    isPeriodic = isTreatmentPeriodic(user_df, treatment_name)
    if isPeriodic:
        return effectivenessInWindow(user_df,treatment_name,symptom_name)
    else:
        for timeframe in TIMEFRAMES:
            effectiveness, certainty = effectivenessAtTime(user_df, treatment_name, symptom_name, timeframe)
            print str(effectiveness) + " with certainty " + str(certainty) + " at time " + str(timeframe)
        return effectiveness, certainty

df = pd.read_csv("flaredown_trackable_data_083016.csv")
df['checkin_date'] = pd.to_datetime(df['checkin_date'])

#user_df = df[df['user_id'] == '2561']
user_df = df[df['user_id'] == 932]
effectiveness, certainty = getEffectiveness(user_df, "alcohol", "Headache")


effectiveness, certainty = getEffectiveness(user_df, "Armodafinil", "Headache")
print str(effectiveness) + " with certainty " + str(certainty)

effectiveness, certainty = getEffectiveness(user_df, "Armodafinil", "Fatigue")
print str(effectiveness) + " with certainty " + str(certainty)