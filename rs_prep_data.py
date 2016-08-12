import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv("flaredown_trackable_data_080316.csv")
df['checkin_date'] = pd.to_datetime(df['checkin_date'])

just_depressed_users = df.groupby(['user_id', 'checkin_date']).filter(lambda x: 'Depression' in x['trackable_name'].values)
#print just_depressed_users.head(20)
#print just_depressed_users[just_depressed_users['trackable_type'] == 'Treatment'].head(20)
def add_depression_score(x):
    return x[x['trackable_name'] == 'Depression']['trackable_value'].values[0]

#just_depressed_users['depression_score'] = just_depressed_users.groupby(['user_id', 'checkin_date']).transform(add_depression_score)
depression_days = just_depressed_users.groupby(['user_id', 'checkin_date'])
depression_scores = depression_days.apply(add_depression_score)
#print depression_scores

just_depressed_users = just_depressed_users[just_depressed_users['trackable_type'] == 'Treatment'].append(just_depressed_users[just_depressed_users['trackable_type'] == 'Tag'])
just_depressed_users = pd.get_dummies(just_depressed_users, columns=['trackable_name'])

#Oh boy this is slow, need to work out a way to do this without the for loop, but haven't gotten to it since it only runs once
#create a matrix of the depression_scores and then .*?
for index, row in just_depressed_users.iterrows():
    depression = depression_scores[int(row['user_id']),row['checkin_date']]
    for i in range(5, len(row)):
        just_depressed_users.loc[index, just_depressed_users.columns[i]] = row[i] * (int(depression) + 1)

just_depressed_users.to_csv('recommender_formatted.csv')
