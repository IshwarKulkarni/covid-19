
"""
Ishwar Kulkarni, 03/31/2020
Given a database connection, fetches the case count based on count/state
and dates and draws some charts for it.
"""

import os
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

import covid_dataset

TABLE_NAME = covid_dataset.TABLE_NAME

def draw_charts(con, q_county=None, q_state=None, num_days=None, min_case_threshold=5):
    """Draws some smooth charts"""

    if not (q_county or q_state):
        return None

    cur = con.cursor()

    if num_days is not None:
        days_filter = f'and d_date>date("now","-{num_days} days")'
    else:
        days_filter = ""

    if q_county and len(q_county) > 0:
        loc_cond = 'county = \"' + q_county + "\" COLLATE NOCASE"
        stmnt = f'select d_date, cases from {TABLE_NAME} d_date where\
                  {loc_cond} {days_filter} order by d_date;'
        title = q_county.title()
    elif q_state and len(q_state) > 0:
        loc_cond = 'state = \"' + q_state + "\" COLLATE NOCASE"
        stmnt = f'select d_date, sum(cases) from {TABLE_NAME} where\
                {loc_cond} {days_filter} group by d_date order by d_date;'
        title = q_state.title()
    else:
        days_filter = "where " + days_filter if len(days_filter) > 0 else days_filter
        stmnt = f'select d_date, sum(cases) from {TABLE_NAME} {days_filter} group by d_date;'
        title = "USA"
        min_case_threshold = 15 # soon going down to zero

    imdir = 'images/' + datetime.now().strftime("%Y-%B-%d")
    img_fn = imdir + "/" + title + ("-" + str(days_filter)  if days_filter else "")+ ".png"
    if os.path.isfile(img_fn):
        return img_fn

    if not os.path.isdir(imdir):
        os.makedirs(imdir)

    cur.execute(stmnt)
    rows = cur.fetchall()
    dates, cases = [], []

    ins = False
    for row in rows:
        if row[1] > min_case_threshold:
            ins = True
        if ins:
            dates.append(row[0])
            cases.append(row[1])

    if len(cases) == 0:
        return None

    fig = plt.figure(num=3, figsize=(16, 9))

    date_start = '/'.join(dates[0].split('-')[-2:])
    date_end = '/'.join(dates[-1].split('-')[-2:])

    gaussian = [0.06136, 0.24477, 0.38774, 0.24477, 0.06136]

    grd_spc = fig.add_gridspec(2, 2)
    plot = fig.add_subplot(grd_spc[0, 0])
    plot.semilogy(cases, 'r-' if(len(cases)) > 20 else 'r-o')
    plot.set_title(f'Cases in {title}|  {date_start} -- {date_end}')
    plot.set_ylabel('log(cases)')

    grad = np.diff(cases)
    plot = fig.add_subplot(grd_spc[0, 1])
    marker = 'g-' if(len(cases)) > 20 else 'g-o'
    plot.semilogy(grad, marker, label="log(New cases)")
    plot.set_title(f'New cases in  {title}|  {date_start} -- {date_end}')

    pct_chng = [d/c * 100 if c > min_case_threshold else 0 for c, d in zip(cases, grad)]
    plot = fig.add_subplot(grd_spc[1, 0])
    plot.plot(np.convolve(pct_chng, gaussian), 'b-' if(len(cases)) > 20 else 'b-o')
    plot.set_title(f'Change% in  {title}|  {date_start} -- {date_end}')

    plot = fig.add_subplot(grd_spc[1, 1])
    plot.loglog(cases[1:], grad, 'r-')
    plot.set_ylabel('log(new cases)')
    plot.set_xlabel('log(cases)')

    fig.savefig(img_fn, dpi=96)
    plt.close(fig)
    return img_fn
