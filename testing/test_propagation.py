from QuietSwarm.Classes.Swarm import Swarm
from QuietSwarm.Helpers.fetchElevationdata import fetchObserverLocation

import numpy as np
import sys
import os


sys.path.append("../QuietSwarm/Orbit_GPU_CPP/build")
import orbit_plotter 


def plotStates_OpenGL(output, energy, nr_sats):
    
    current_file_path = os.path.abspath(__file__) # Sökväg till test_propagation.py
    testing_dir = os.path.dirname(current_file_path) # mappen 'testing'
    project_root = os.path.dirname(testing_dir)
    
    vert_shader_path = os.path.join(project_root, "QuietSwarm/Orbit_GPU_CPP", "shader.vert")
    frag_shader_path = os.path.join(project_root, "QuietSwarm/Orbit_GPU_CPP", "shader.frag")
    
    total_punkter = len(output)
    n_stride = total_punkter // nr_sats
    
    indices = np.arange(total_punkter).reshape((n_stride, nr_sats)).flatten(order='F')
    
    sorted_output = output[indices]
    sorted_energy = energy[indices]
    
    x_flat = sorted_output['x'].tolist()
    y_flat = sorted_output['y'].tolist()
    z_flat = sorted_output['z'].tolist()
    h_flat = sorted_energy.tolist()
    
    # Normalize Energy tracking array array context boundary limits to a transparent 0.0 - 1.0 scope
    e_min, e_max = min(h_flat), max(h_flat)
    if e_max > e_min:
        normalized_energy = [(e - e_min) / (e_max - e_min) for e in h_flat]
    else:
        normalized_energy = [0.5] * len(h_flat)

    print("Transferring data arrays over to active GPU instances...")
    
    
    orbit_plotter.plot_ecef(
        x_flat, 
        y_flat, 
        z_flat, 
        normalized_energy,
        vert_shader_path,
        frag_shader_path 
    )


def main():
    dt          = 0.01
    tmax        = 1000
    
    # n_steps     = int(tmax // dt)
    # stride      = int((1.0 / tau) // dt)
    
    UT1 = "2026-05-10 16:05:00"
    orbitalfile = "test.dat"
    
    
    observer     = (18.172604, 59.405896)
    diff         = 0.1

    
    _, observer = fetchObserverLocation(observer, diff)
    
    
    swarm       = Swarm(orbitalfile)
    output      = swarm.propagate(tmax=tmax, dt=dt)
    
    
    states_ecef = swarm.eciToecef(UT1, output)
    states_azel = swarm.ecefToAzEl(states_ecef, observer)
    states_lla  = swarm.eciTolla(states_ecef)
    
    plotStates_OpenGL(output, output["H"], swarm.nr_sats)
    
    
    
    
if __name__ == "__main__":
    main()
