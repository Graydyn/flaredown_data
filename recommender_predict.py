### Usage: python recommender_predict.py datafile modeldir <pearson|cosine>
### Example: python recommender_predict.py test_user_1.csv models
### Example: python recommender_predict.py test_user_1.csv models pearson

### Takes in a single user's effectiveness measurements and determines what the most and least effect treatements for them will be

import numpy as np
import pandas as pd
import sys
import functools
import warnings
warnings.filterwarnings("ignore")

if len(sys.argv) < 3:
    print "Usage: python recommender_predict.py datafile modelfile distance_metric"
    quit()

file = sys.argv[1]
modeldir = sys.argv[2]

test_df = pd.read_csv(file)

distance_metric = 'cosine'
if len(sys.argv) == 4:
    if (sys.argv[3] == 'pearson') or (sys.argv[3] == 'cosine'):
        distance_metric = sys.argv[3]
    else:
        print "distance metric must be pearson or cosine"
        quit()

#get a list of all the conditions this user has
#we will search each of them to see which one is most actionable
#I'm just taking the highest and lowest predicted effectiveness for all conditions, could just as easily return a recommendation per condition
conditions = list(set(test_df['condition']))

highestPredictedValue = 0
highestPredictedKey = ""
highestPredictedCondition = ""
lowestPredictedValue = 0
lowestPredictedKey = ""
lowestPredictedCondition = ""
for condition in conditions:
    condition_rows = test_df[test_df['condition'] == condition]
    correlations = pd.read_csv(modeldir + '/' + condition.replace('/', '').replace("\n","").replace("\r","") + "_" + distance_metric + ".csv")

    # some treatments won't have any associated distances, just skip over them
    #correlations = correlations.dropna(how='all',axis=1)

    #looking for the max values for pearson (from -1 to 1 with 1 being closest)
    #but looking for min values for cosine (from 0-2 with 0 being closest)
    best_fit_predicted_effectiveness = 0
    best_fit_treatment_name = ""
    if (distance_metric == 'pearson'):
        condition_rows['closest_correlation_name'] = condition_rows['treatment'].apply(
            lambda x: correlations[correlations['row'] == x].drop('row', axis=1).idxmax(axis=1).values[0])
        condition_rows['closest_correlation_value'] = condition_rows['treatment'].apply(
            lambda x: correlations[correlations['row'] == x].drop('row', axis=1).max(axis=1).values[0])
        condition_rows = condition_rows[pd.notnull(condition_rows['closest_correlation_value'])]
        if len(condition_rows) > 0:
            tiedRows = condition_rows[
                condition_rows['closest_correlation_value'] == condition_rows['closest_correlation_value'].max()]
            best_fit_predicted_effectiveness = condition_rows.ix[tiedRows['effectiveness'].abs().idxmax()]['effectiveness']
            best_fit_treatment_name = condition_rows.ix[tiedRows['effectiveness'].abs().idxmax()]['closest_correlation_name']
    else:
        condition_rows['closest_correlation_name'] = condition_rows['treatment'].apply(
            lambda x: correlations[correlations['row'] == x].drop('row', axis=1).idxmin(axis=1).values[0])
        condition_rows['closest_correlation_value'] = condition_rows['treatment'].apply(
            lambda x: correlations[correlations['row'] == x].drop('row', axis=1).min(axis=1).values[0])
        condition_rows = condition_rows[pd.notnull(condition_rows['closest_correlation_value'])]
        if len(condition_rows) > 0:
            tiedRows = condition_rows[condition_rows['closest_correlation_value'] == condition_rows['closest_correlation_value'].min()]
            #in the case of a tie, go with the most relevant predicted effectiveness
            best_fit_predicted_effectiveness = condition_rows.ix[tiedRows['effectiveness'].abs().idxmax()]['effectiveness']
            best_fit_treatment_name = condition_rows.ix[tiedRows['effectiveness'].abs().idxmax()]['closest_correlation_name']

    #Now we know which treatment that the user has tried has another treatment which is most highly correlated to it, so predict that
    #the new treatment will have an effectiveness similar to the original treatment
    if best_fit_treatment_name not in test_df['treatment'].values: #a check to make sure we don't recommend a treatment they already use
        if highestPredictedValue < best_fit_predicted_effectiveness:
            highestPredictedValue = best_fit_predicted_effectiveness
            highestPredictedName = best_fit_treatment_name
            highestPredictedCondition = condition
        if lowestPredictedValue > best_fit_predicted_effectiveness:
            lowestPredictedValue = best_fit_predicted_effectiveness
            lowestPredictedName = best_fit_treatment_name
            lowestPredictedCondition = condition

madeRec = False
if highestPredictedValue > 0:
    print "This user may have good results treating " + highestPredictedCondition + " with " + highestPredictedName
    madeRec = True
if lowestPredictedValue < 0:
    madeRec = True
    print "This user may have good results treating " + lowestPredictedCondition + " by staying away from " + lowestPredictedName
if not madeRec:
    print "We have no reliable recommendation to make for this user"