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

    K = 19 #VCU
    # K = 15 #CGW
    # K = 23 #SCU
    N=100
    ConfidenceLevel = 0.95

    df = pd.read_csv('bitstuffing0_VCU_running0.csv', skiprows=1)
    N=26
    for i in range(0,N):
        if (i == 0):
            pdfs = calculate_pdf(df.iloc[:,[2*i, 2*i+1]], 0, K)
        else:
            pdfs = pd.concat([pdfs, calculate_pdf(df.iloc[:,[2*i, 2*i+1]], 0, K)])

    df = pd.read_csv('bitstuffing0_VCU_running1.csv', skiprows=1)
    N=25
    for i in range(0,N):
        if (i == 0):
            pdfs = pd.concat([pdfs, calculate_pdf(df.iloc[:,[2*i, 2*i+1]], 0, K)])
        else:
            pdfs = pd.concat([pdfs, calculate_pdf(df.iloc[:,[2*i, 2*i+1]], 0, K)])
    
    df = pd.read_csv('bitstuffing0_VCU_running2.csv', skiprows=1)
    N=25
    for i in range(0,N):
        if (i == 0):
            pdfs = pd.concat([pdfs, calculate_pdf(df.iloc[:,[2*i, 2*i+1]], 0, K)])
        else:
            pdfs = pd.concat([pdfs, calculate_pdf(df.iloc[:,[2*i, 2*i+1]], 0, K)])
    df = pd.read_csv('bitstuffing0_VCU_running3.csv', skiprows=1)
    N=24
    for i in range(0,N):
        if (i == 0):
            pdfs = pd.concat([pdfs, calculate_pdf(df.iloc[:,[2*i, 2*i+1]], 0, K)])
        else:
            pdfs = pd.concat([pdfs, calculate_pdf(df.iloc[:,[2*i, 2*i+1]], 0, K)])
    
    N = 100
    stddev = pdfs.std()
    zAlpha = stats.t.ppf(1-(1-ConfidenceLevel)/2, N-1)
    samplemeanpdf = pd.DataFrame({'x': range(0,K+1), 'y': pdfs.mean()})
    lower = samplemeanpdf['y'] - zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    upper = samplemeanpdf['y'] + zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    
    errors = [[m-l for l,m in zip(lower,samplemeanpdf['y'])]]
    errors.append([u-m for u,m in zip(upper,samplemeanpdf['y'])])

    items = ['Idle', 'Scheduler', 'Source application', 'Sink application',
             'Driver controls fast', 'CAN receive','Driver Controls slow','Exterior lighting',
             'Window wiper','Cameras','Horn manager','Solar control','Power steering','Vehicle power',
             'AVAS','CAN transmit','Thermal management','Thermal slow','Background',
             'Version']
    # items = ['Idle', 'Scheduler', 'Source application', 'Sink application',
    #          'Closures fast', 'LIN', 'CAN receive', 'Authentication', 'Exterior lighting',
    #          'Closures slow', 'Driver controls', 'Vehicle Power', 'CAN transmit', 
    #          'Firmware Upgrade', 'Background', 'Version']
    # items = ['Idle', 'Scheduler', 'Source application', 'Sink application', 
    #          'Safety Supervisor', 'Energy Controller fast', 'gsl', 'amg', 'sai',
    #          'Closures fast', 'Propulsion fast', 'Propulsion safety', 'CAN receive', 'Vehicle Power', 
    #          'Energy Controller slow', 'DCM', 'Exterior Lighting', 'Closures slow',
    #          'Battery Management', 'CAN transmit', 'Window wiper', 'STM', 
    #          'Background', 'Version']
             
    # ax = samplemeanpdf.plot(kind='scatter', x='x', y='y', legend=True, label="Sample pdf", xlabel='Size', ylabel='Probability')
    # plt.errorbar(samplemeanpdf['x'], samplemeanpdf['y'], yerr=errors, fmt='none', capsize=8, ecolor='red')
    # plt.xticks(range(0,K+1, 2))
    # plt.rcParams['ytick.major.pad'] = '10'

    size = set_size(424.58624)
    plt.figure(figsize=(size[0], size[1]*1.4))
    plt.grid(visible=True, alpha=0.7)
    plt.barh(samplemeanpdf['x'],samplemeanpdf['y'], xerr=errors,capsize=5, ecolor='red')
    plt.xlabel('Utilization')
    
    xlim=0.05 #VCU
    # xlim=0.3 #CGW
    # xlim=0.2 #SCU
    plt.xlim(0, xlim)
    plt.yticks(range(0,K+1,1),items)
    plt.tight_layout()
    plt.rcParams.update({"font.family": "serif",  # use serif/main font for text elements
    "text.usetex": True,     # use inline math for ticks
    "pgf.rcfonts": False     # don't setup fonts from rc parameters
    })
    plt.savefig('utilization_vcu_100.pgf', format='pgf')
    plt.show()