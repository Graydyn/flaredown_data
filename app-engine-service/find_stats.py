# It would use a lot of resources to do these calculations every time somebody hits the API
# So generating figures for every condition and then loading onto google cloud store

#need to authenticate before running by setting an environment variable to your keyfile like:
#export GOOGLE_APPLICATION_CREDENTIALS=Flaredown-24ac7b1e7653.json

#if updating, be sure to delete old records first or you will get duplicates

import numpy as np
import pandas as pd
import random
from google.cloud import datastore
import json

def create_client():
    project_id = 'flaredown-149515'
    return datastore.Client(project_id)

def add_trackable(client, trackable_type, dict):
    key = client.key('Condition'+trackable_type)
    trackable_entity = datastore.Entity(
        key)

    trackable_entity.update(dict)
    client.put(trackable_entity)
    return trackable_entity.key

def add_condition_list(client, conditions):
    key = client.key('ConditionList')
    for condition in conditions:
        trackable_entity = datastore.Entity(
        key)

        trackable_entity.update({
            "name": condition,
        })
        client.put(trackable_entity)
    return trackable_entity.key

def add_trackable_count(client, trackable_type, trackable_name, count):
    key = client.key(trackable_type+"Count")
    trackable_entity = datastore.Entity(
        key)

    trackable_entity.update({
        "name" : trackable_name,
        "count" : count
    })
    client.put(trackable_entity)
    return trackable_entity.key

df = pd.read_csv("flaredown_trackable_data_080316.csv")
df['checkin_date'] = pd.to_datetime(df['checkin_date'])

anno_df = pd.read_csv("conditions_list.csv")
conditions_set = set(anno_df['New Name'])
conditions_set = set(filter(lambda x: x == x, conditions_set)) #remove nan

def writeConditionCounts(client, trackable_type):
    trackables = set(df[df['trackable_type'] == trackable_type]['trackable_name'])
    trackables = list(set(filter(lambda x: x == x, trackables)))  # remove nan

    for condition in conditions_set:
        print trackable_type + ' ' + condition
        trackable_dict = {}
        trackable_dict['condition'] = condition
        trackable_dict['id'] = condition
        names = anno_df[anno_df['New Name'] == condition]['Condition'].values

        #condition_df = df[df['trackable_name'].isin(names)]
        condition_df = df.groupby(['user_id']).filter(lambda x: len(set(x['trackable_name'].values) & set(names)) > 0)
        for trackable in trackables:
            trackable_df = condition_df[condition_df['trackable_name'] == trackable]
            trackable_clean = ''.join(trackable.split("\n"))
            trackable_clean = ''.join(trackable_clean.split(","))
            trackable_dict[trackable_clean] = len(trackable_df.groupby('user_id'))
        key = add_trackable(client,trackable_type,trackable_dict)
        print key


def writeCounts(client, trackable_type):
    trackables = set(df[df['trackable_type'] == trackable_type]['trackable_name'])
    trackables = list(set(filter(lambda x: x == x, trackables)))  # remove nan
    for trackable in trackables:
        trackable_clean = ''.join(trackable.split("\n"))
        trackable_clean = ''.join(trackable_clean.split(","))
        trackable_df = df[df['trackable_name'] == trackable].groupby('user_id')
        num_of_users = len(trackable_df)
        add_trackable_count(client, trackable_type, trackable_clean, num_of_users)

client = create_client()
#writeConditionCounts(client, 'Symptom')
#writeConditionCounts(client,'Condition')
#writeConditionCounts(client,'Treatment')
writeConditionCounts(client,'Tag')

#add_condition_list(client,conditions_set)

#writeCounts(client,'Symptom')
#writeCounts(client,'Condition')
#writeCounts(client,'Treatment')
#writeCounts(client,'Tag')