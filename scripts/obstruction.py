import os
import argparse
import h5py

from QuietSwarm.Classes.Swarm import Swarm


def main(filepath):
    with h5py.File(filepath, "r+") as f:
        if "states_ecef" not in f:
            raise KeyError("Dataset 'states_ecef' was not found in the HDF5 file. It is required!")
        
        if "elevation_map" not in f:
            raise KeyError("Dataset 'elevation_map' was not found in the HDF5 file. It is required!")
        
        states_ecef = f["states_ecef"]
        observer    = f["elevation_map"]

        
        swarm = Swarm()
        obstructed = swarm.obstruction(states_ecef, observer)
        
        
        
        
        
        

if __name__ == "__main__":
    print('''
              -------------------------------------------------------------
                    Helper-script for calculating obstruction
              -------------------------------------------------------------
              Script requires an existing HDF5 with existing orbitalConfigs.
              Run writeConfiguration.py if you don't have such a file yet!
              ''')
        
    path     = os.getcwd()
    parser = argparse.ArgumentParser(description="Obstruction.")
    parser.add_argument("--filename", type=str, required=True, help="Name of hdf5 file")
    
    
    args = parser.parse_args()
        
    filepath = os.path.join(path,args.filename)
    
    if not os.path.isfile(filepath) or not h5py.is_hdf5(filepath):
        raise ValueError(f"'{args.filename}' does not exist or is not a valid HDF5 file.")
    
    main(filepath)