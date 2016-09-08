## The recommender gives more sensible results if you remove tags that aren't actionable.
## By actionable I mean something the user can do something about.  For example "Feeling Blah" isn't actionably, we
## don't want to recommend avoiding "Feeling Blah" because that's not useful information

## Running this file will add any new tags to the file, which will then need to be hand labelled.
## Since most tags are not actionable, I'm defaulting them to off(0) until somebody comes and turns them on

import pandas as pd

df = pd.read_csv("flaredown_trackable_data_080316.csv")

tags = list(set(df[df['trackable_type'] == 'Tag']['trackable_name']))
relevance = pd.read_csv("tag_relevance.csv")
existing_tags = list(set(relevance['tag']))
outfile = open('tag_relevance.csv', 'a')
print existing_tags
for tag in tags:
    if (tag not in existing_tags) and (not ',' in str(tag)):
        outfile.write(str(tag) + ",0\n")