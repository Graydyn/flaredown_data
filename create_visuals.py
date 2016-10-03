import numpy as np
import pandas as pd
import sys
import functools
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

orig_df = pd.read_csv("flaredown_trackable_data_083016.csv")
orig_df = orig_df[orig_df['user_id'] == 52]
orig_df['checkin_date'] = pd.to_datetime(orig_df['checkin_date'])
#orig_df['trackable_value'] = pd.to_numeric(orig_df['trackable_value'])

test_df = pd.read_csv("effectiveness_test.csv")

treatments = orig_df[orig_df['trackable_type'] == "Treatment"]

orig_df = orig_df[orig_df['trackable_name'] == "Insomnia"]
orig_df['trackable_value'] = pd.to_numeric(orig_df['trackable_value'])

#datetime.strptime("2012-may-31 19:00", "%Y-%b-%d %H:%M")
#datetime.datetime(2012, 5, 31, 19, 0)

fig1 = False

if fig1:
    #orig_df.plot('checkin_date', 'trackable_value')
    #fig, (ax1, ax2) = plt.subplots(1,2, sharex=True, sharey=True)
    plt.plot(orig_df['checkin_date'].values, orig_df['trackable_value'].values)
    plot_margin = 0.25
    x0, x1, y0, y1 = plt.axis()
    plt.axis((x0 - plot_margin,x1 + plot_margin,y0 - plot_margin,y1 + plot_margin))
    plt.ylabel('Symptom Rating')
    plt.xlabel('Date')
    red_patch = mpatches.Patch(color='red', alpha = 0.2, label='Escitalopram')
    plt.legend(handles=[red_patch])

    blue_patch = mpatches.Patch(color='blue', alpha = 0.2, label='Magnesium')
    plt.legend(handles=[red_patch,blue_patch], loc=2)

    esca_start = '2016-06-30'
    esca_end = '2016-07-24'
    #ax2.fill_between(esca_start, 0, esca_end, facecolor='blue', alpha=0.5)
    #ax2 = plt.gca()
    #ax2.add_patch(Rectangle((0.4, 0.4), 0.2, 0.2, fill=None, alpha=1))

    plt.savefig("test.png")

fig2 = False

if fig2:
    insomnia = test_df[test_df['condition'] == "Insomnia"]
    width = 0.2
    index = np.arange(2)
    fig, ax = plt.subplots()
    ax.bar(index, insomnia['effectiveness'].values, width)
    ax.set_xticklabels(('Escitalopram', 'Magnesium'))
    ax.set_xticks(index + width / 2)
    plot_margin = 0.25
    x0, x1, y0, y1 = plt.axis()
    plt.axis((x0 - plot_margin, x1 + plot_margin, y0, y1 + plot_margin))
    plt.ylabel('Effectiveness Against Insomnia')
    plt.xlabel('Treatment')
    plt.savefig("workflow2.png")

fig3 = False
if fig3:
    insomnia = test_df[test_df['condition'] == "Insomnia"]
    width = 0.2
    index = np.arange(2)
    fig, ax = plt.subplots()
    ax.bar(index, insomnia['effectiveness'].values, width, color='y')
    ax.set_xticklabels(('Wellbutrin', 'Iron'))
    ax.set_xticks(index + width / 2)
    plot_margin = 0.25
    x0, x1, y0, y1 = plt.axis()
    plt.axis((x0 - plot_margin, x1 + plot_margin, y0, y1 + plot_margin))

    plt.ylabel('Predicted Effectiveness Against Insomnia')
    plt.xlabel('Treatment')
    #plt.show()
    plt.savefig("workflow3.png")

fig4 = True
if fig4:

    #got these values from doing a dump out of predict.py
    esca_corr = [1.0,0.3,0.7]
    mag_corr = [0,0,1]

    width = 0.1
    index = np.arange(3)
    fig, ax = plt.subplots()
    ax.bar(index, esca_corr, width, color='r')
    ax.bar(index + width, mag_corr, width, color='b')
    ax.set_xticklabels(('Wellbutrin','Sertraline','Iron'))
    ax.set_xticks(index + width / 2)
    plot_margin = 0.25
    x0, x1, y0, y1 = plt.axis()
    plt.axis((x0 - plot_margin, x1 + plot_margin, y0, y1 + plot_margin))

    red_patch = mpatches.Patch(color='red', label='Escitalopram')

    blue_patch = mpatches.Patch(color='blue', label='Magnesium')
    plt.legend(handles=[red_patch, blue_patch], loc=2)

    plt.ylabel('Correlation to Target Treatment')
    plt.xlabel('Treatment')
    #plt.show()
    plt.savefig("workflow4.png")