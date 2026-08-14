import os
import argparse
import h5py
import numpy as np

from QuietSwarm.Classes.ElevationData import TerrestrialGrid

def main(filepath, country, clear_cache):
    
    terrestrial = TerrestrialGrid(country=country.lower())
   
    grid = terrestrial.generate_gridpoints(nr_points=100)
    
    print("----------------- Downloading dems -------------------")
    grid = terrestrial.fetch_dem_heights(grid)
    
    lon, lat = grid["geometry"].x, grid["geometry"].y
    height   = grid["height"]
    
    structured_dtype = np.dtype([("lon", "<f8"), ("lat", "<f8"), ("height", "<f8")])
    data = np.zeros(len(grid), dtype=structured_dtype)
    
    data["lon"] = grid["geometry"].x.values
    data["lat"] = grid["geometry"].y.values
    data["height"] = grid["height"].values
    
    print("----------------- Writing to hdf5 -------------------")
    with h5py.File(filepath, "r+") as f:
        if "elevation_map" in f:
            del f["elevation_map"]
        
        elev_map_dset = f.create_dataset("elevation_map",
                                         shape=data.shape,
                                         dtype=data.dtype)
        
        elev_map_dset[:] = data
    
    print("Finished!")
    
    if clear_cache:
        print("----------------- Clearing cache -------------------")
        terrestrial.topo._clear_cache()
        print("Finished")
    

if __name__ == "__main__":
    print('''
              -------------------------------------------------------------
                    Helper-script for retrieving terrestrial grid
              -------------------------------------------------------------
              Script requires an existing HDF5 with existing orbitalConfigs.
              Run writeConfiguration.py if you don't have such a file yet!
              ''')
        
    path     = os.getcwd()
    parser = argparse.ArgumentParser(description="Propagation.")
    parser.add_argument("--filename", type=str, required=True, help="Name of hdf5 file")
    parser.add_argument("--country", type=str, required=True, help="Name of country border")
    parser.add_argument("--clear_cache", action="store_true", required=False, default=False, help="clear cache")
    args = parser.parse_args()
    
    filepath = os.path.join(path,args.filename)
    
    if not os.path.isfile(filepath) or not h5py.is_hdf5(filepath):
            raise ValueError(f"'{args.filename}' does not exist or is not a valid HDF5 file.")
    
    country = args.country
    
    clear_cache = args.clear_cache
    main(filepath=filepath, country=country,clear_cache=clear_cache)