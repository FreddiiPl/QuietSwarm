import os
import argparse
import h5py
import numpy as np
import time

from QuietSwarm.Classes.Swarm import Swarm


def main(filepath, tmax, dt, nr_threads, ecef=False, geo=False, topo=False, utc=None,):
    with h5py.File(filepath, "r+") as f:
            if "orbitalConfigs" not in f:
                raise KeyError("Dataset 'orbitalConfigs' was not found in the HDF5 file.")
            
            configs = f['orbitalConfigs']
            headers = list(configs.attrs["headers"])
            
            ctypes_order = [
            "sat_id", "raan", "argp", "incl_rad", "phases_rad", "sma", "ecc"
            ]
            
            reordered_data = []
            for key in ctypes_order:
                idx = headers.index(key)
                reordered_data.append(configs[idx])
                
            params = np.array(reordered_data).T
            print(params.shape)
            start = time.time()
            swarm = Swarm(params=params)
            output      = swarm.propagate(tmax=tmax, dt=dt, nr_threads=nr_threads)
            end = time.time()
            
            print(f"Runtime: {(end - start):.4f} seconds")
            if "states_eci" in f:
                del f["states_eci"]
            
            eci_dset = f.create_dataset("states_eci", 
                                        shape=output.shape, 
                                        dtype=output.dtype)         
            eci_dset[:] = output
            
            
            if ecef:
                states_ecef = swarm.eciToecef(state_eci=output)
                
                if "states_ecef" in f:
                    del f["states_ecef"]
                
                ecef_dset = f.create_dataset("states_ecef",
                                             shape=states_ecef.shape,
                                             dtype=states_ecef.dtype
                                             )
                
                ecef_dset[:] = states_ecef
            
            
            if geo:
                states_geo = swarm.eciTolla(output)
                
                if "states_geo" in f:
                    del f["states_geo"]
                
                geo_dset = f.create_dataset("states_geo",
                                            shape=states_geo.shape,
                                            dtype=states_geo.dtype)
                
                geo_dset[:] = states_geo
            
            # to be implemented
            if topo:
                if "observerLocations" not in f:
                    raise KeyError("Dataset 'observerLocations' was not found in the HDF5 file.")
                
                pass
            
            
    


if __name__=="__main__":
    print('''
          -------------------------------------------------------------
                Helper-script for calculating propagated orbits
          -------------------------------------------------------------
          Script requires an existing HDF5 with existing orbitalConfigs.
          Run writeConfiguration.py if you don't have such a file yet!
          ''')
    
    path     = os.getcwd()
    parser = argparse.ArgumentParser(description="Propagation.")
    parser.add_argument("--filename", type=str, required=True, help="Name of hdf5 file")
    parser.add_argument("--tmax", type=float, required=True, help="Max propagation time!")
    parser.add_argument("--dt", type=float, required=True, help="propagation timestep!")
    
    # threading
    parser.add_argument("--nr_threads", type=int, default=1, required=False, help="for multithreading")
    
    # optional states
    parser.add_argument("--ecef", action="store_true", default=False, help="compute and store ecef states")
    parser.add_argument("--geo", action="store_true", default=False, help="compute and store geographic states")
    parser.add_argument("--topo", action="store_true", default=False, help="compute and store topographic states")
    
    args = parser.parse_args()
    
    filepath = os.path.join(path,args.filename)
    
    
    if not os.path.isfile(filepath) or not h5py.is_hdf5(filepath):
        raise ValueError(f"'{args.filename}' does not exist or is not a valid HDF5 file.")
    
    ecef = args.ecef
    geo  = args.geo
    topo = args.topo
    
    tmax     = args.tmax
    dt       = args.dt
    
    nr_threads = args.nr_threads
    main(filepath, tmax=tmax, dt=dt, nr_threads=nr_threads, ecef=ecef, geo=geo, topo=topo)
    