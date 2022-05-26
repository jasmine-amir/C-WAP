#!/usr/bin/env python3

import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
import sys
import pandas as pd
import numpy as np


if len(sys.argv) != 4:
    raise Exception('Incorrect call to the script.')


# Data regarding the current sample passed by UNIX
freyjaOutputFile = sys.argv[1]
freyjaBootFile = sys.argv[2]
outfilename = sys.argv[3]


# Translation table for pangolin and WHO names of variants
pangolin2WHO = {'B.1.1.7': 'Alpha', 'B.1.351': 'Beta', 'P.1': 'Gamma', 'B.1.427': 'Epsilon', 'B.1.429': 'Epsilon',
                'B.1.525': 'Eta', 'B.1.526': 'Iota', 'B.1.617.1': 'Kappa', 'B.1.621': 'Mu', 'B.1.621.1': 'Mu',
                'P.2': 'Zeta', 'B.1.617.3': 'B.1.617.3', 'B.1.617.2': 'Delta', 'AY': 'Delta',
                'B.1.1.529': 'Omicron', 'BA.1': 'BA.1', 'BA.2': 'BA.2', 'BA.2.12': 'BA.2.12',
                'BA.3': 'BA.3', 'wt': 'wt', 'wt-wuhan': 'wt',
                'A.21': 'Bat', 'other': 'Other', 'A': 'wt', 'Error':'Error'}


# Convert each variant to a WHO-compatible name, if one exists
def getDisplayName(pangolinName):
    if pangolinName in pangolin2WHO.keys():
        # Exact correspondance to a published name
        return pangolin2WHO[pangolinName]
    elif pangolinName in pangolin2WHO.values():
        # Already an exact match to a published name
        return pangolinName
    else:
        # Check if this is a sublineage of a defined lineage
        for i in range(pangolinName.count('.'), 0, -1):
            superVariant = '.'.join(pangolinName.split('.')[0:i])
            if superVariant in pangolin2WHO:
                return pangolin2WHO[superVariant]

        # No name seems to correspond to it, return itself
        return pangolinName


# Assign a pre-determined color to each display name
rgbColors = plt.get_cmap('tab20b').colors + plt.get_cmap('tab20c').colors[0:16]
colorCycle = [to_hex(color) for color in rgbColors]
def getColor (var_name):
    if var_name.lower() == 'other':
        return '#BBBBBB'
    else:
        color_idx = hash(var_name)%len(colorCycle)
        return colorCycle[color_idx]


# Process the bootstrap result table generated by Freyja
freyja_boot = pd.read_table(freyjaBootFile, index_col=0, header=0, sep=',')
boot_names = [ getDisplayName(x) for x in list(freyja_boot) ]

percentiles = list(freyja_boot.index)
index25 = percentiles.index(0.25)
index50 = percentiles.index(0.50)
index75 = percentiles.index(0.75)
percentile25 = list(freyja_boot.iloc[index25])
percentile50 = list(freyja_boot.iloc[index50])
percentile75 = list(freyja_boot.iloc[index75])

 
 
########################################################
# Process the original abundance estimates by Freyja
freyja_raw = pd.read_table(freyjaOutputFile, index_col=0)

# Import the detailed subvariant breakdown
lineages = eval( pd.Series(freyja_raw.loc['lineages'][0])[0].replace(' ', ',') )
abundances = eval( ','.join(pd.Series(freyja_raw.loc['abundances'][0])[0].split()) )
freyja_names = [ getDisplayName(x) for x in lineages ]

freyja_hits = []
for dname in set(freyja_names):
    pct = 100 * sum([ y for (x,y) in zip(freyja_names, abundances) if x==dname ])
    median = 100 * sum([ y for (x,y) in zip(boot_names, percentile50) if x==dname ])
    spread = 100 * np.sqrt(sum([ (z-y)**2 for (x,y,z) in zip(boot_names, percentile25, percentile75) if x==dname ]))   
    freyja_hits.append( (dname, pct, median, spread) )


# Make a scatter plot, value vs. estimated spread
plt.rcParams.update({'font.size': 14})

for (dname, pct, median, spread) in freyja_hits:
    color2plot = getColor(dname)
    plt.plot(pct, median, 'o', color=color2plot)
    plt.errorbar(pct, median, yerr=3*spread, color=color2plot)
    plt.text(pct+np.random.randint(0,5), median+np.random.randint(0,5), dname, color=color2plot)


plt.plot([0,100], [0,100], 'k--')
plt.axis('tight')
plt.xlim(0, 100)
plt.ylim(0, 100)
plt.xlabel('Freyja demix prediction')
plt.ylabel('Freyja boot median +/- 3 FWHM')
plt.title('Freyja bootstrapping')

plt.savefig(outfilename, dpi=300)
plt.close()
