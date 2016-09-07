### Usage: python recommender_predict.py datafile modeldir <pearson|cosine>
### Example: python recommender_predict.py effectiveness_test.csv models
### Example: python recommender_predict.py effectiveness_test.csv models pearson

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

#run through each treatment that the user has tried and find the highest correlatation value to any of them
def find_closest_pearson(treatment_correlations, x):
    highestCorrelationValue = -2 #lowest possible correlation is -1
    highestCorrelationKey = ""
    for treatment1 in x:
        if treatment1 in treatment_correlations:
            treatment2_index = treatment_correlations[treatment1].idxmax(axis=1)
            treatment2_value = treatment_correlations[treatment1][treatment2_index]
            treatment2_key = treatment_correlations.iloc[treatment2_index]['row']
            if treatment2_value > highestCorrelationValue:
                highestCorrelationValue = treatment2_value
                highestCorrelationKey = treatment2_key
    return str(highestCorrelationValue) + ":" + highestCorrelationKey

#just like above, except in this case the lowest value is the closest distance
def find_closest_cosine(treatment_correlations, x):
    highestCorrelationValue = 3 #highest possible distance is 2
    highestCorrelationRecommendedTreatment = ""
    highestCorrelationUserTreatment = ""
    for treatment1 in x:
        treatment_correlations.dropna(how='all', axis=1)  #some treatments won't have any associated distances, just skip over them
        if treatment1 in treatment_correlations:
            treatment2_index = treatment_correlations[treatment1].idxmin(axis=1)
            treatment2_value = treatment_correlations[treatment1][treatment2_index]
            treatment2_key = treatment_correlations.iloc[treatment2_index]['row']
            if treatment2_value < highestCorrelationValue:
                highestCorrelationValue = treatment2_value
                highestCorrelationRecommendedTreatment = treatment2_key
                highestCorrelationUserTreatment = treatment1
    return str(highestCorrelationValue) + ":" + highestCorrelationRecommendedTreatment + ":" + highestCorrelationUserTreatment

#Need to send two values back from my transform, so bundling them and then splittng them afterwards
#TODO gotta be a better way...
def unpack_value(x):
    return x.split(":")[0]
def unpack_recommended_treatment(x):
    return x.split(":")[1]
def unpack_user_treatment(x):
    return x.split(":")[2]
#get a list of all the conditions this user has
#we will search each of them to see which one is most actionable
conditions = list(set(test_df['condition']))

#I'm just taking the highest and lowest predicted effectiveness for all conditions, could just as easily do this per condition
highestPredictedValue = 0 
highestPredictedKey = ""
highestPredictedCondition = ""
lowestPredictedValue = 0
lowestPredictedKey = ""
lowestPredictedCondition = ""
for condition in conditions:
    condition_rows = test_df[test_df['condition'] == condition]
    correlations = pd.read_csv(modeldir + '/' + condition.replace('/', '').replace("\n","").replace("\r","") + "_" + distance_metric + ".csv")

    if (distance_metric == 'pearson'):
        find_closest_func = functools.partial(find_closest_pearson,correlations) #this is so I can pass an argument into my transform function
    else:
        find_closest_func = functools.partial(find_closest_cosine,correlations)
    condition_rows['closest_correlation'] = condition_rows.groupby('user_id')['treatment'].transform(find_closest_func).values

    condition_rows['recommended_treatment_value'] = condition_rows['closest_correlation'].apply(unpack_value)
    condition_rows['recommended_treatment_name'] = condition_rows['closest_correlation'].apply(unpack_recommended_treatment)
    condition_rows['recommended_user_treatment'] = condition_rows['closest_correlation'].apply(unpack_user_treatment)
    print condition_rows
    #Now we know which treatment that the user has tried has another treatment which is most highly correlated to it, so predict that
    #the new treatment will have an effectiveness similar to the original treatment
    predicted_value = condition_rows[condition_rows['treatment'] == condition_rows['recommended_user_treatment']]['effectiveness'].values
    if highestPredictedValue < predicted_value:
        highestPredictedValue = predicted_value
        highestPredictedKey = condition_rows['recommended_treatment_name']
        highestPredictedCondition = condition
    if lowestPredictedValue > predicted_value:
        lowestPredictedValue = predicted_value
        lowestPredictedKey = condition_rows['recommended_treatment_name']
        lowestPredictedCondition = condition

if highestPredictedValue > 0:
    print "This user may have good results treating " + highestPredictedCondition + " with " + highestPredictedKey
if lowestPredictedValue < 0:
    print "This user may have good results treating " + lowestPredictedCondition + " by staying away from " + lowestPredictedKey