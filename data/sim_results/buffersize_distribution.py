#!/usr/bin/env python3
import argparse
import pandas as pd
import os
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np

def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)
    
# sum the duration for a given buffer size , add total duration in last column
# 0, 1, 2, ..., 55, time
def calc_duration(df, lower, upper):
    df = df.dropna()
    if df.isnull().values.any():
        print("oopsiedoodle")
        exit()

    pdf = []
    T = df.iloc[:,0].max() - df.iloc[:,0].min() # Simulation time length
    dtime = df.iloc[:,0].diff().iloc[1:].reset_index(drop=True)
    data = df.iloc[:,1][:-1]
    minimalObservedSize = int(max(df.iloc[:,1].min(), lower))
    maximalObservedSize = int(min(df.iloc[:,1].max(), upper))

    for i in range(0, minimalObservedSize):
        pdf.append(0)
    
    # For each nr of elements in the system (interval), calculate the total time spent in that interval
    # an interval includes the left point and excludes the right point, at the edges (min,max) the
    # interval size is only half.
    for i in range(minimalObservedSize, maximalObservedSize + 1):
        pdf.append(dtime.dot(data == i))

    for i in range(0, upper-maximalObservedSize):
        pdf.append(0)

    pdf.append(T)

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
    df = pd.read_csv(file, skiprows=1)

    N = 20
    K = 55
    counts = pd.DataFrame(0, index=np.arange(57), dtype='float64', columns=[2, 10, 16,48])
    # df.loc[0, 2] = 42
    # print(df.head())

    for i in range(0,N):
        if (i == 0):
            pdfs2 = calc_duration(df.iloc[:, 40:42], 0, K)
        else:
            pdfs2 = pd.concat([pdfs2, calc_duration(df.iloc[:,[40+2*i,41+2*i]], 0, K)])

    counts.loc[:,2] = pdfs2.sum()
    
    for i in range(0,N):
        if (i == 0):
            pdfs10 = calc_duration(df.iloc[:, 200:202], 0, K)
        else:
            pdfs10 = pd.concat([pdfs10, calc_duration(df.iloc[:,[200+2*i,201+2*i]], 0, K)])
    counts.loc[:,10] = pdfs10.sum()

    for i in range(0,N):
        if (i == 0):
            pdfs16 = calc_duration(df.iloc[:, 240:242], 0, K)
        else:
            pdfs16 = pd.concat([pdfs16, calc_duration(df.iloc[:,[240+2*i,241+2*i]], 0, K)])
    counts.loc[:,16] = pdfs16.sum()

    for i in range(0,N):
        if (i == 0):
            pdfs48 = calc_duration(df.iloc[:, 280:282], 0, K)
        else:
            pdfs48 = pd.concat([pdfs48, calc_duration(df.iloc[:,[280+2*i,281+2*i]], 0, K)])
    counts.loc[:,48] = pdfs48.sum()

    percentage = counts.iloc[0:K+1,:].div(counts.iloc[K+1, :])
    
    plt.figure(figsize=set_size(424.58624))
    plt.plot(range(K+1), percentage, label=['Hardware buffer size 2','Hardware buffer size 10','Hardware buffer size 16','Hardware buffer size 48'])
    plt.xlabel("Nr of messages in SCU powertrain CAN bus software buffer")
    plt.ylabel("Percentage of total simulation time")
    plt.legend()
    plt.rcParams.update({"font.family": "serif",  # use serif/main font for text elements
    "text.usetex": True,     # use inline math for ticks
    "pgf.rcfonts": False     # don't setup fonts from rc parameters
    })
    plt.savefig('buffersize_dist.pgf', format='pgf')
    plt.show()  