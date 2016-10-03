### Usage: python recommender_train.py datafile modeldir <pearson|cosine> threshold
### Example: python recommender_train.py effectiveness_083016.csv models
### Example: python recommender_train.py effectiveness_083016.csv models pearson 0.05

### This script takes in the pre-processed datafile from treatment_effectiveness.ipynb and measures the cosine distance
### between the effectiveness of all tags/treatments.  It then outputs a cosine distance table for each condition, which
### can be used by recommender_predict.py

### Before deciding on a distance metric, check out the accompanying notebook.  Long story short, you will find more
### non-na distances if you use cosine distance, but pearson is more discriminant.  If you set the
### distance metric to pearson, you can also set a p value to use as a threshold for significance.  At this time
### (August 31st, 2016) if you use pearson and set a p value threshold of 0.05 you will find 0 significant correlations.

### Don't be surprised by the amount of NaN in the model.  Only treatments/tags that have been used by the same user
### for the same condition will have a value.  This means that most values will be NaN.

import numpy as np
import pandas as pd
import sys
from scipy.spatial import distance
from scipy.stats.stats import pearsonr

if len(sys.argv) < 3:
    print "Usage: python recommender_train.py datafile modelfile"
    quit()

file = sys.argv[1]
modeldir = sys.argv[2]

distance_metric = 'cosine'
if len(sys.argv) >= 4:
    if (sys.argv[3] == 'pearson') or (sys.argv[3] == 'cosine'):
        distance_metric = sys.argv[3]
    else:
        print "distance metric must be pearson or cosine"
        quit()
threshold = 0.05
if len(sys.argv) == 5:
    threshold = sys.argv[4]

df = pd.read_csv(file)

def find_distances(condition_rows, treatment, other_treatments, condition):
    treatment_correlations = {}
    treatment_correlations['row'] = treatment
    for treatment2 in other_treatments:
        users_with_treatment2 = list(set(condition_rows[condition_rows['treatment'] == treatment2]['user_id']))
        treatment1_values = condition_rows[(condition_rows['user_id'].isin(users_with_treatment2)) & (condition_rows['treatment'] == treatment)]['effectiveness']
        treatment2_values = condition_rows[(condition_rows['user_id'].isin(users_with_treatment2)) & (condition_rows['treatment'] == treatment2)]['effectiveness']
        if (not np.isnan(treatment1_values).any()) and (not np.isnan(treatment2_values).any()):
            if distance_metric == 'cosine':
                cos_distance = distance.cosine(treatment1_values, treatment2_values)
                treatment_correlations[treatment2] = cos_distance
            else: #pearson
                if len(treatment1_values) > 1 : #can't compare scalars in pearson
                    pearson_result = pearsonr(treatment1_values, treatment2_values)
                    correlation = pearson_result[0]
                    if pearson_result[1] < threshold:
                        treatment_correlations[treatment2] = correlation
    return treatment_correlations

conditions = list(set(df['condition']))
for condition in conditions:
    print "finding table for " + condition
    #get a list of all treatments/tags that have been reported at the same time as this condition
    treatments = list(set(df[df['condition'] == condition]['treatment']))

    #empty dataframe with each treatment/tag as a column, will fill with each treatment/tag as a row to make square matrix
    result = pd.DataFrame(columns=treatments)

    for treatment in treatments:
        #the list of all users that have reported both the condition and target treatment
        affected_users = list(set(df[(df['treatment'] == treatment) & (df['condition'] == condition)]['user_id']))
        affected_rows = df[(df['user_id'].isin(affected_users)) & (df['condition'] == condition)]

        other_treatments = affected_rows[affected_rows['treatment'] != treatment]['treatment']
        distances = find_distances(affected_rows, treatment, other_treatments, condition)
        result = result.append(distances, ignore_index=True)

    result.to_csv(modeldir + '/' + condition.replace('/', '').replace("\n","").replace("\r","") + "_" + distance_metric + ".csv", index=False)