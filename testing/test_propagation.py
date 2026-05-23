from QuietSwarm.Classes.Swarm import Swarm
from QuietSwarm.Helpers.fetchElevationdata import fetchObserverLocation


import matplotlib.pyplot as plt
import matplotlib as mpl

import os
from dotenv import load_dotenv

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
    dt          = 0.01
    tmax        = 2000
    n_steps     = int(tmax // dt)
    stride      = 1
    
    UT1 = "2026-05-10 16:05:00"
    orbitalfile = "test.dat"
    
    
    observer     = (18.172604, 59.405896)
    diff         = 0.1

    
    _, observer = fetchObserverLocation(observer, diff)
    
    
    swarm = Swarm(orbitalfile)
    output      = swarm.propagate(n_steps=n_steps, dt=dt,stride=stride)
    states_ecef = swarm.eciToecef(UT1, output)
    states_azel = swarm.ecefToAzEl(states_ecef, observer)
    states_lla  = swarm.eciTolla(states_ecef)
    
    # correct result?
    fig = plt.figure(figsize=(12,8))
    
    ax0 = fig.add_subplot(141)
    ax0.scatter(states_azel['az'], states_azel['el'])
    ax0.set_ylim(-90, 90)
    ax0.set_xlabel("Azimuth (deg)")
    ax0.set_ylabel("Elevation (deg)")
    
    ax1 = fig.add_subplot(142)
    ax1.scatter(states_lla["longitude"], states_lla["latitude"])
    ax1.set_xlabel("Longitude (deg)")
    ax1.set_ylabel("Latitude (deg)")
    
    ax2  = fig.add_subplot(143,projection="3d")
    ax2.scatter(output['x'], output['y'], output['z'])
    ax2.set_title("ECI")
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    ax2.set_zlabel("z")
    
    ax3  = fig.add_subplot(144,projection="3d")
    ax3.scatter(states_ecef['x'], states_ecef['y'] , states_ecef['z'])
    ax3.set_title("ECEF")
    ax3.set_xlabel("x")
    ax3.set_ylabel("y")
    ax3.set_zlabel("z")
    
    
    
    plt.show()
    
    
if __name__ == "__main__":
    main()
