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
    df = pd.read_csv(file, skiprows=1)

    N = 20
    ConfidenceLevel = 0.95
    
    K = 55
    for i in range(0,N):
        if (i == 0):
            pdfs1 = calculate_pdf(df.iloc[:, 0:2], 0, K)
        else:
            pdfs1 = pd.concat([pdfs1, calculate_pdf(df.iloc[:,[2*i,2*i+1]], 0, K)])
    
    for i in range(0,N):
        if (i == 0):
            pdfs2 = calculate_pdf(df.iloc[:, 40:42], 0, K)
        else:
            pdfs2 = pd.concat([pdfs2, calculate_pdf(df.iloc[:,[40+2*i,41+2*i]], 0, K)])

    for i in range(0,N):
        if (i == 0):
            pdfs4 = calculate_pdf(df.iloc[:, 80:82], 0, K)
        else:
            pdfs4 = pd.concat([pdfs4, calculate_pdf(df.iloc[:,[80+2*i,81+2*i]], 0, K)])  
    
    for i in range(0,N):
        if (i == 0):
            pdfs6 = calculate_pdf(df.iloc[:, 120:122], 0, K)
        else:
            pdfs6 = pd.concat([pdfs6, calculate_pdf(df.iloc[:,[120+2*i,121+2*i]], 0, K)])
    
    for i in range(0,N):
        if (i == 0):
            pdfs8 = calculate_pdf(df.iloc[:, 160:162], 0, K)
        else:
            pdfs8 = pd.concat([pdfs8, calculate_pdf(df.iloc[:,[160+2*i,161+2*i]], 0, K)])
    

    for i in range(0,N):
        if (i == 0):
            pdfs10 = calculate_pdf(df.iloc[:, 200:202], 0, K)
        else:
            pdfs10 = pd.concat([pdfs10, calculate_pdf(df.iloc[:,[200+2*i,201+2*i]], 0, K)])

    for i in range(0,N):
        if (i == 0):
            pdfs16 = calculate_pdf(df.iloc[:, 240:242], 0, K)
        else:
            pdfs16 = pd.concat([pdfs16, calculate_pdf(df.iloc[:,[240+2*i,241+2*i]], 0, K)])


    for i in range(0,N):
        if (i == 0):
            pdfs48 = calculate_pdf(df.iloc[:, 280:282], 0, K)
        else:
            pdfs48 = pd.concat([pdfs48, calculate_pdf(df.iloc[:,[280+2*i,281+2*i]], 0, K)])

    plt.figure(figsize=set_size(424.58624))
    

    # means = pd.DataFrame({'x': range(0,K+1), 'y': pdfs1.mean()})
    # samplemeanpdf = means[means['y'] > 0.00001]
    size=12
    samplemeanpdf = pd.DataFrame({'x': range(0,K+1), 'y': pdfs2.mean()})
    stddev = pdfs2.std()
    zAlpha = stats.t.ppf(1-(1-ConfidenceLevel)/2, N-1)
    lower = samplemeanpdf['y'] - zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    upper = samplemeanpdf['y'] + zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    
    samplemeanpdf = pd.concat([samplemeanpdf, lower.rename('lower')], axis=1)
    samplemeanpdf = pd.concat([samplemeanpdf, upper.rename('upper')], axis=1)
    
    samplemeanpdf = samplemeanpdf[samplemeanpdf['y']>0.0]
    errors = [[m-l for l,m in zip(samplemeanpdf['lower'],samplemeanpdf['y'])]]
    errors.append([u-m for u,m in zip(samplemeanpdf['upper'],samplemeanpdf['y'])])
    
    kwargs = {'zorder': 0}
    plt.scatter(samplemeanpdf['x'], samplemeanpdf['y'],s=size,label='Hardware buffer size 2')
    plt.errorbar(samplemeanpdf['x'], samplemeanpdf['y'], yerr=errors,fmt='none', ecolor='black', capsize=3, **kwargs)
    plt.xticks(range(0,60, 4))
    plt.grid(visible=True, alpha=0.7)

    # means = pd.DataFrame({'x': range(0,K+1), 'y': pdfs2.mean()})
    # samplemeanpdf = means[means['y'] > 0.00001]
    samplemeanpdf = pd.DataFrame({'x': range(0,K+1), 'y': pdfs10.mean()})
    stddev = pdfs10.std()
    zAlpha = stats.t.ppf(1-(1-ConfidenceLevel)/2, N-1)
    lower = samplemeanpdf['y'] - zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    upper = samplemeanpdf['y'] + zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    
    samplemeanpdf = pd.concat([samplemeanpdf, lower.rename('lower')], axis=1)
    samplemeanpdf = pd.concat([samplemeanpdf, upper.rename('upper')], axis=1)
    
    samplemeanpdf = samplemeanpdf[samplemeanpdf['y']>0.0]
    errors = [[m-l for l,m in zip(samplemeanpdf['lower'],samplemeanpdf['y'])]]
    errors.append([u-m for u,m in zip(samplemeanpdf['upper'],samplemeanpdf['y'])])
    plt.scatter(samplemeanpdf['x'], samplemeanpdf['y'],s=size,label='Hardware buffer size 10')
    plt.errorbar(samplemeanpdf['x'], samplemeanpdf['y'], yerr=errors,fmt='none', ecolor='black', capsize=3, **kwargs)

    # samplemeanpdf = pd.DataFrame({'x': range(0,K+1), 'y': pdfs4.mean()})
    # stddev = pdfs4.std()
    # zAlpha = stats.t.ppf(1-(1-ConfidenceLevel)/2, N-1)
    # lower = samplemeanpdf['y'] - zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    # upper = samplemeanpdf['y'] + zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    
    # errors = [[m-l for l,m in zip(lower,samplemeanpdf['y'])]]
    # errors.append([u-m for u,m in zip(upper,samplemeanpdf['y'])])
    # #plt.scatter(samplemeanpdf['x'], samplemeanpdf['y'])
    # plt.errorbar(samplemeanpdf['x'], samplemeanpdf['y'], yerr=errors, label='Hardware buffer size 4')

    samplemeanpdf = pd.DataFrame({'x': range(0,K+1), 'y': pdfs16.mean()})
    stddev = pdfs16.std()
    zAlpha = stats.t.ppf(1-(1-ConfidenceLevel)/2, N-1)
    lower = samplemeanpdf['y'] - zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    upper = samplemeanpdf['y'] + zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    
    samplemeanpdf = pd.concat([samplemeanpdf, lower.rename('lower')], axis=1)
    samplemeanpdf = pd.concat([samplemeanpdf, upper.rename('upper')], axis=1)
    
    samplemeanpdf = samplemeanpdf[samplemeanpdf['y']>0.0]
    errors = [[m-l for l,m in zip(samplemeanpdf['lower'],samplemeanpdf['y'])]]
    errors.append([u-m for u,m in zip(samplemeanpdf['upper'],samplemeanpdf['y'])])
    plt.scatter(samplemeanpdf['x'], samplemeanpdf['y'],s=size,label='Hardware buffer size 16')
    plt.errorbar(samplemeanpdf['x'], samplemeanpdf['y'], yerr=errors, fmt='none', ecolor='black',capsize=3, **kwargs)

    # samplemeanpdf = pd.DataFrame({'x': range(0,K+1), 'y': pdfs8.mean()})
    # stddev = pdfs8.std()
    # zAlpha = stats.t.ppf(1-(1-ConfidenceLevel)/2, N-1)
    # lower = samplemeanpdf['y'] - zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    # upper = samplemeanpdf['y'] + zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    
    # errors = [[m-l for l,m in zip(lower,samplemeanpdf['y'])]]
    # errors.append([u-m for u,m in zip(upper,samplemeanpdf['y'])])
    # #plt.scatter(samplemeanpdf['x'], samplemeanpdf['y'])
    # plt.errorbar(samplemeanpdf['x'], samplemeanpdf['y'], yerr=errors, label='Hardware buffer size 8')

    # samplemeanpdf = pd.DataFrame({'x': range(0,K+1), 'y': pdfs10.mean()})
    # stddev = pdfs10.std()
    # zAlpha = stats.t.ppf(1-(1-ConfidenceLevel)/2, N-1)
    # lower = samplemeanpdf['y'] - zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    # upper = samplemeanpdf['y'] + zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    
    # errors = [[m-l for l,m in zip(lower,samplemeanpdf['y'])]]
    # errors.append([u-m for u,m in zip(upper,samplemeanpdf['y'])])
    # #plt.scatter(samplemeanpdf['x'], samplemeanpdf['y'])
    # plt.errorbar(samplemeanpdf['x'], samplemeanpdf['y'], yerr=errors, label='Hardware buffer size 10')

    # samplemeanpdf = pd.DataFrame({'x': range(0,K+1), 'y': pdfs16.mean()})
    # stddev = pdfs16.std()
    # zAlpha = stats.t.ppf(1-(1-ConfidenceLevel)/2, N-1)
    # lower = samplemeanpdf['y'] - zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    # upper = samplemeanpdf['y'] + zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    
    # errors = [[m-l for l,m in zip(lower,samplemeanpdf['y'])]]
    # errors.append([u-m for u,m in zip(upper,samplemeanpdf['y'])])
    # #plt.scatter(samplemeanpdf['x'], samplemeanpdf['y'])
    # plt.errorbar(samplemeanpdf['x'], samplemeanpdf['y'], yerr=errors, label='Hardware buffer size 16')

    samplemeanpdf = pd.DataFrame({'x': range(0,K+1), 'y': pdfs48.mean()})
    stddev = pdfs48.std()
    zAlpha = stats.t.ppf(1-(1-ConfidenceLevel)/2, N-1)
    lower = samplemeanpdf['y'] - zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    upper = samplemeanpdf['y'] + zAlpha*((stddev.pow(2)).div(N)).pow(0.5)
    samplemeanpdf = pd.concat([samplemeanpdf, lower.rename('lower')], axis=1)
    samplemeanpdf = pd.concat([samplemeanpdf, upper.rename('upper')], axis=1)
    
    samplemeanpdf = samplemeanpdf[samplemeanpdf['y']>0.0]
    errors = [[m-l for l,m in zip(samplemeanpdf['lower'],samplemeanpdf['y'])]]
    errors.append([u-m for u,m in zip(samplemeanpdf['upper'],samplemeanpdf['y'])])
    plt.scatter(samplemeanpdf['x'], samplemeanpdf['y'],s=size,label='Hardware buffer size 48')
    plt.errorbar(samplemeanpdf['x'], samplemeanpdf['y'], yerr=errors,  fmt='none' ,ecolor='black',capsize=3, **kwargs)
    plt.xlabel("Nr of messages in SCU powertrain CAN bus software buffer")
    plt.ylabel("Probability")
    plt.legend()
    plt.rcParams.update({"font.family": "serif",  # use serif/main font for text elements
    "text.usetex": True,     # use inline math for ticks
    "pgf.rcfonts": False     # don't setup fonts from rc parameters
    })
    plt.savefig('buffersize.pgf', format='pgf')
    plt.show()