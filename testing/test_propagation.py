from QuietSwarm.Classes.Swarm import Swarm
from QuietSwarm.Helpers.fetchElevationdata import fetchObserverLocation


import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

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

def darkkWrapper(f):
    def wrapper(*args, **kwargs):
        plt.style.use('dark_background')
        return f(*args, **kwargs)
    return wrapper


def plotECEFstates(fig, states_ecef, energy):
    ax3  = fig.add_subplot(111,projection="3d")
    sc = ax3.scatter(states_ecef['x'] / 1e3, states_ecef['y']  / 1e3 , states_ecef['z']  / 1e3 , c=energy, cmap="Spectral_r")
    ax3.set_title("ECEF")
    ax3.set_xlabel("x (km)")
    ax3.set_ylabel("y (km)")
    ax3.set_zlabel("z (km)")
    
    ax3.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax3.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax3.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    
    ax3.grid(False)
    ax3.set_box_aspect([1, 1, 1])
    
    max_range = np.max(np.abs(np.concatenate((states_ecef['x'], states_ecef['y'], states_ecef['z'])))) / 1e3
    max_range *= 1.05

    ax3.set_xlim([-max_range, max_range])
    ax3.set_ylim([-max_range, max_range])
    ax3.set_zlim([-max_range, max_range])
    
    ax3.view_init(elev=30, azim=45)
    
    plt.colorbar(sc)


@darkkWrapper
def main():
    dt          = 0.01
    tmax        = 1000
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
    

    fig = plt.figure(figsize=(12,8))
    plotECEFstates(fig, states_ecef, output["H"])
    plt.tight_layout()
    plt.savefig("propagation_output.png", dpi=300)
    
    
if __name__ == "__main__":
    main()
