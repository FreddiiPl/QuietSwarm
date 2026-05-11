from QuietSwarm.Classes.Swarm import Swarm


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
    dt          = 0.01
    tmax        = 2000
    n_steps     = int(tmax // dt)
    stride      = 1
    
    
    orbitalfile = "test.dat"
    
    swarm = Swarm(orbitalfile)
    
    UT1 = "2026-05-10 16:05:00"
    # swarm.eciToecef(UT1)
    output      = swarm.propagate(n_steps=n_steps, dt=dt,stride=stride)
    states_ecef = swarm.eciToecef(UT1, output)
    # swarm.compute_geometry(...) # to be written
    
    
    fig = plt.figure(figsize=(12,8))
    ax  = fig.add_subplot(projection="3d")
    
    ax.scatter(output['x'], output['y'], output['z'])
    
    plt.show()
    
    
if __name__ == "__main__":
    main()
