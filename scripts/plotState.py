import os
import argparse
import h5py

import geopandas as gpd

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


FRAME_DATASETS = {
    "eci": "states_eci",
    "ecef": "states_ecef",
    "geographic": "states_geo",
    "topocentric": "states_topo"
}

from pathlib import Path
script_dir = Path(__file__).resolve().parent


def load_state_data(states, ref_frame):
    if ref_frame in ("eci", "ecef"):
        return {
            "u": states["x"] / 1e3,
            "v": states["y"] / 1e3,
            "w": states["z"] / 1e3,
            "H": states["H"],
            "is3d": True,
            "labels": ("x (km)", "y (km)", "z (km)")
        }
    
    if ref_frame == "geographic":
        return {
            "u": states['longitude'],
            "v": states['latitude'],
            "H": states["H"],
            "is3d": False,
            "xlim": [-180, 180],
            "ylim": [-90, 90],
            "background": gpd.read_file(script_dir / "../QuietSwarm/Files/CNTR_RG_01M_2024_4326.gpkg"),
            "labels": ("Longitude (deg)", "Latitude (deg)")
        }
    
    return {
        "u": states["az"],
        "v": states["el"],
        "H": states["H"],
        "is3d": False,
        "xlim": [0, 360],
        "ylim": [0, 90],
        "background": None,
        "labels": ("Azimuth (deg)", "Elevation (deg)")
    }
    

def plot_3d(data):
    fig = plt.figure(figsize=(12,8))
    ax = fig.add_subplot(projection="3d")
    
    sc = ax.scatter(
        data["u"],
        data["v"],
        data["w"],
        s=1,
        c=data["H"],
        cmap="plasma_r"
    )
    
    ax.set_xlabel(data["labels"][0])
    ax.set_ylabel(data["labels"][1])
    ax.set_zlabel(data["labels"][2])
    
    plt.colorbar(sc, ax=ax)
    plt.tight_layout()
    plt.show()


def plot_2d(data, grid):
    
    initial_H = data["H"][0]
    padding = abs(initial_H) * 0.0001 
    
    fig = plt.figure(figsize=(18,8))
    ax = fig.add_subplot()
    
    if data["background"] is not None:
        data["background"].plot(ax=ax, color="black", linewidth=1)
    
    sc = ax.scatter(
        data["u"],
        data["v"],
        s=1,
        c=data["H"],
        cmap="plasma_r",
        vmin=initial_H - padding,
        vmax=initial_H + padding
    )
    
    if grid is not None:
        ax.scatter(
                x=grid["lon"],
                y=grid["lat"],
                s=1,
                c=grid["height"],
                cmap="terrain"
            )
    
    
    ax.set_xlabel(data["labels"][0])
    ax.set_ylabel(data["labels"][1])
    
    ax.set_xlim(data["xlim"])
    ax.set_ylim(data["ylim"])
    plt.colorbar(sc, ax=ax, label=r"Hamiltonian $H$ (J$\cdot$kg$^{-1}$)")
    plt.tight_layout()
    plt.show()


def plot_hamiltonian(data):
    initial_H = data["H"][0]
    fig, ax = plt.subplots(figsize=(12,8))
    ax.axhline(y=initial_H, linestyle="--", linewidth=2, color="k", label="Initial H")
    
    ax.plot(data["t"], data["H"], linewidth=2, color="b", label="Simulation H")
    
    padding = abs(initial_H) * 0.0001
    ax.set_ylim(initial_H - padding, initial_H + padding)
    
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(r"Hamiltonian energy (J$\cdot$kg$^{-1}$)")
    
    ax.legend()
    
    
    
    plt.tight_layout()
    plt.show()
    

def plot_grid(grid):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    ax.scatter(
        x=grid["lon"],
        y=grid["lat"],
        s=10,
        c=grid["height"],
        cmap="plasma_r"
    )
    
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    
    plt.tight_layout()
    plt.show()


def main(filepath, ref_frame, hamiltonian, grid):
    
    with h5py.File(filepath, "r") as f:
        if "states_eci" not in f:
            raise KeyError("Dataset 'states_eci' was not found in the HDF5 file.")
        
        states = f[FRAME_DATASETS[ref_frame]]
        data = load_state_data(states, ref_frame)

        if data["is3d"]:
            plot_3d(data)
        else:
            if grid:
                if "elevation_map" not in f:
                    raise KeyError(f"{filepath} does not contain a dem grid!")
                
                grid = f["elevation_map"]
            
            else:
                
                grid = None
                
            plot_2d(data,grid=grid)
        
        
        if hamiltonian:
            plot_hamiltonian(states)
            
        # if grid:
        #     if "elevation_map" not in f:
        #         raise KeyError(f"{filepath} does not contain a dem grid!")
            
        #     grid = f["elevation_map"]
        #     plot_grid(grid)
   
   
        

if __name__ == "__main__":
    print('''
              -------------------------------------------------------------
                    Helper-script for plotting state
              -------------------------------------------------------------
              Script requires an existing HDF5 with existing orbitalConfigs.
              Run writeConfiguration.py if you don't have such a file yet!
              ''')
    
    path     = os.getcwd()
    parser = argparse.ArgumentParser(description="Plot.")
    parser.add_argument("--filename", type=str, required=True, help="Name of hdf5 file")
    parser.add_argument("--ref_frame", type=str, default="eci", choices=FRAME_DATASETS.keys(), required=False, help="Reference frame!")
    parser.add_argument("--hamiltonian", action="store_true", default=False, help="for diagnostics")
    parser.add_argument("--grid", action="store_true", default=False, help="for diagnostics")
    
    args = parser.parse_args()
    filepath = os.path.join(path,args.filename)
    
    if not os.path.isfile(filepath) or not h5py.is_hdf5(filepath):
        raise ValueError(f"'{args.filename}' does not exist or is not a valid HDF5 file.")
    
    ref_frame = args.ref_frame
    
    hamiltonian = args.hamiltonian
    grid        = args.grid
    
    main(filepath, ref_frame, hamiltonian=hamiltonian, grid=grid)