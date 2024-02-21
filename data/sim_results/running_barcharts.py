#!/usr/bin/env python3
import argparse
import pandas as pd
import os
from scipy import stats
import matplotlib.pyplot as plt

def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)
    
def calculate_pdf(df, lower, upper):
    df = df.dropna()
    if df.isnull().values.any():
        print("oopsiedoodle")
        exit()
    pdf = []
    T = df["time"].max() - df["time"].min() # Simulation time length
    dtime = df["time"].diff().iloc[1:].reset_index(drop=True)
    data = df["size"][:-1]
    minimalObservedSize = int(max(df["size"].min(), lower))
    maximalObservedSize = int(min(df["size"].max(), upper))
    for i in range(0, minimalObservedSize):
        pdf.append(0)
    
    # For each nr of elements in the system (interval), calculate the total time spent in that interval
    # an interval includes the left point and excludes the right point, at the edges (min,max) the
    # interval size is only half.
    for i in range(minimalObservedSize, maximalObservedSize + 1):
        pdf.append(dtime.dot(data == i) / T)
    
    for i in range(0, upper-maximalObservedSize):
        pdf.append(0)

    return pd.DataFrame([pdf])

def set_size(width_pt, fraction=1, subplots=(1, 1)):
    """Set figure dimensions to sit nicely in our document.

    Parameters
    ----------
    width_pt: float
            Document width in points
    fraction: float, optional
            Fraction of the width which you wish the figure to occupy
    subplots: array-like, optional
            The number of rows and columns of subplots.
    Returns
    -------
    fig_dim: tuple
            Dimensions of figure in inches
    """
    # Width of figure (in pts)
    fig_width_pt = width_pt * fraction
    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    golden_ratio = (5**.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio * (subplots[0] / subplots[1])

    return (fig_width_in, fig_height_in)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', type=file_path)
    args = parser.parse_args()
    file = args.csv

    K = 19
    N=10
    ConfidenceLevel = 0.95

    df = pd.read_csv(file, names=['t0','0','t1', '1', 't2','2', 't3','3', 't4','4', 't5','5', 't6','6', 't7','7', 't8','8', 't9','9'], skiprows=1)
    for i in range(0,N):
        time = 't{}'.format(i)
        running = str(i)
        if (i == 0):
            pdfs = calculate_pdf(df[[time,running]].rename(columns={time: "time", running: 'size'})
                                 , 0, K)
        else:
            pdfs = pd.concat([pdfs, calculate_pdf(df[[time,running]].rename(columns={time: "time", running: 'size'}), 0, K)])

    samplemeanpdf = pd.DataFrame({'x': range(0,K+1), 'y': pdfs.mean()})

    stddev = pdfs.std()
    zAlpha = stats.t.ppf(1-(1-ConfidenceLevel)/2, N-1)
    lower = samplemeanpdf['y'] - zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    upper = samplemeanpdf['y'] + zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    
    errors = [[m-l for l,m in zip(lower,samplemeanpdf['y'])]]
    errors.append([u-m for u,m in zip(upper,samplemeanpdf['y'])])

    items = ['Idle', 'Scheduler', 'Source application', 'Sink application',
             'dcm_vcu_10_ms_task', 'gwy_receive_task','dcm_vcu_task','exl_control_task_vcu',
             'wiper_manager_task','cmm_task','hmg_task','sol_task','stm_task','vpc_vcu_task_50ms',
             'avs_task','gwy_transmit_task','tms_100ms_task','tms_task_500ms','psc_background_app',
             'version_transmitter']
    # ax = samplemeanpdf.plot(kind='scatter', x='x', y='y', legend=True, label="Sample pdf", xlabel='Size', ylabel='Probability')
    # plt.errorbar(samplemeanpdf['x'], samplemeanpdf['y'], yerr=errors, fmt='none', capsize=8, ecolor='red')
    # plt.xticks(range(0,K+1, 2))
    # plt.rcParams['ytick.major.pad'] = '10'
    plt.figure(figsize=set_size(0.95*424.58624))
    plt.grid(visible=True, alpha=0.7)
    plt.barh(samplemeanpdf['x'],samplemeanpdf['y'], xerr=errors,capsize=8, ecolor='red')
    plt.xlabel('Utilization')
    plt.yticks(range(0,K+1,1),items)
    plt.tight_layout()
    plt.rcParams.update({"font.family": "serif",  # use serif/main font for text elements
    "text.usetex": True,     # use inline math for ticks
    "pgf.rcfonts": False     # don't setup fonts from rc parameters
    })
    plt.savefig('utilization.pgf', format='pgf')
    plt.show()