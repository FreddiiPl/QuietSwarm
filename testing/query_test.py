from QuietSwarm.Helpers.fetchElevationdata import fetchObserverLocation
from dotenv import load_dotenv
import os

import matplotlib.pyplot as plt
import matplotlib as mpl

# Default figure settings
mpl.rcParams['axes.linewidth'] = 1.2
mpl.rcParams['xtick.direction'] = "in"
mpl.rcParams['xtick.top'] = True
mpl.rcParams['ytick.direction'] = "in"
mpl.rcParams['ytick.right'] = True
mpl.rcParams['xtick.minor.visible'] = True
mpl.rcParams['ytick.minor.visible'] = True
mpl.rcParams['font.weight'] = "bold"
mpl.rcParams['axes.labelweight'] = "bold"
mpl.rcParams['font.size'] = 12

def main():
    load_dotenv("...")
    

    observer     = (18.172604, 59.405896)
    diff         = 0.1

    data, observer = fetchObserverLocation(observer, diff)
    
    fig, ax = plt.subplots(figsize=(12,8))
    ax.imshow(data[0], extent=data[1], cmap="terrain")
    
    plt.show()
    
    


if __name__ == "__main__":
    main()