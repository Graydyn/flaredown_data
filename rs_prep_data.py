import numpy as np
import pandas as pd
from scipy.stats.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

#When you can get this down to 0.05 and still get some results, then we're getting somewhere
P_THRESHOLD = 0.3

df = pd.read_csv("flaredown_trackable_data_080316.csv")
df['checkin_date'] = pd.to_datetime(df['checkin_date'])

just_depressed_users = df.groupby(['user_id', 'checkin_date']).filter(lambda x: 'Depression' in x['trackable_name'].values)
def add_depression_score(x):
    return x[x['trackable_name'] == 'Depression']['trackable_value'].values[0]
#just_depressed_users['depression_score'] = just_depressed_users.groupby(['user_id', 'checkin_date']).transform(add_depression_score)
depression_days = just_depressed_users.groupby(['user_id', 'checkin_date'])

#create a table of depression scores by user/day
depression_scores = depression_days.apply(add_depression_score)
depression_scores = depression_scores.reset_index()
depression_scores.columns = ["user_id", "checkin_date", "depression_score"]
#add that table to the dataframe

just_depressed_users = just_depressed_users[just_depressed_users['trackable_type'] == 'Treatment'].append(just_depressed_users[just_depressed_users['trackable_type'] == 'Tag'])
#just_depressed_users = just_depressed_users[just_depressed_users['trackable_type'] == 'Treatment']
just_depressed_users = pd.get_dummies(just_depressed_users, columns=['trackable_name'])

just_depressed_users = just_depressed_users.merge(depression_scores, on=['user_id','checkin_date'])
just_depressed_users['depression_score'] = pd.to_numeric(just_depressed_users['depression_score'])

print "writing file"
userlist = set(just_depressed_users['user_id'])
outfile = open('recommender_formatted.csv', 'w')
outfile.write('user_id,')
outfile.write(','.join(list(just_depressed_users.columns[5:len(just_depressed_users.columns) - 1])))
outfile.write("\n")
for userid in userlist:
    user = just_depressed_users[just_depressed_users['user_id'] == userid]
    first = True
    outfile.write(str(userid))
    #print np.correlate(user['depression_score'], user['trackable_name_tired'])
    for column in user.columns[5:len(user.columns)-1]:
        corr,p =  pearsonr(user['depression_score'], user[column])
        if (p < P_THRESHOLD):
            outfile.write(',' + str(corr))
        else:
            outfile.write(',0')
    outfile.write("\n")
            #print "for column " + column
            #print "    got correlation " + str(corr) + " with p value " + str(p)
#just_depressed_users.to_csv('recommender_formatted.csv')
