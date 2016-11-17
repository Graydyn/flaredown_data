# It would use a lot of resources to do these calculations every time somebody hits the API
# So generating figures for every condition and then loading onto google cloud store

import numpy as np
import pandas as pd
import random
from google.cloud import datastore

def create_client(project_id):
    return datastore.Client(project_id)

def add_trackable(client, trackable_type):
    key = client.key('Condition-'+trackable_type)

    task = datastore.Entity(
        key, exclude_from_indexes=['description'])

    task.update({
        'condition': datetime.datetime.utcnow(),
        'description': description,
        'done': False
    })

    client.put(task)

    return task.key

df = pd.read_csv("flaredown_trackable_data_080316.csv")
df['checkin_date'] = pd.to_datetime(df['checkin_date'])

anno_df = pd.read_csv("conditions_list.csv")
conditions_set = set(anno_df['New Name'])
conditions_set = set(filter(lambda x: x == x, conditions_set)) #remove nan

def writeCSV(trackable_type):
    outfile = open(trackable_type + '_count_by_condition.csv', 'w')
    outfile.write('Condition,')
    trackables = set(df[df['trackable_type'] == trackable_type]['trackable_name'])
    trackables = list(set(filter(lambda x: x == x, trackables)))  # remove nan

    for trackable in trackables:
        trackable_clean = ''.join(trackable.split("\n"))
        trackable_clean = ''.join(trackable_clean.split(","))
        outfile.write(trackable_clean + ',')
    outfile.write("\n")
    for condition in conditions_set:
        print condition
        names = anno_df[anno_df['New Name'] == condition]['Condition'].values

        #condition_df = df[df['trackable_name'].isin(names)]
        condition_df = df.groupby(['user_id']).filter(lambda x: len(set(x['trackable_name'].values) & set(names)) > 0)
        outfile.write(condition + ',')
        for trackable in trackables:
            trackable_df = condition_df[condition_df['trackable_name'] == trackable]
            outfile.write(str(len(trackable_df.groupby('user_id'))) + ",")
        outfile.write("\n")

def writeCounts(trackable_type):
    outfile = open(trackable_type + '_counts.csv', 'w')
    trackables = set(df[df['trackable_type'] == trackable_type]['trackable_name'])
    trackables = list(set(filter(lambda x: x == x, trackables)))  # remove nan
    for trackable in trackables:
        trackable_clean = ''.join(trackable.split("\n"))
        trackable_clean = ''.join(trackable_clean.split(","))
        trackable_df = df[df['trackable_name'] == trackable].groupby('user_id')
        num_of_users = len(trackable_df)
        outfile.write(trackable_clean + ',' + str(num_of_users) + "\n")

writeCSV('Symptom')
writeCSV('Condition')
writeCSV('Treatment')
writeCSV('Tag')

#writeCounts('Symptom')
#writeCounts('Condition')
#writeCounts('Treatment')
#writeCounts('Tag')