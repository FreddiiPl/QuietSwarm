import os
import argparse
import numpy as np
import h5py
from QuietSwarm.Helpers.wgs84 import EARTH_SEMI_MAJOR_AXIS



def configurateOrbits(data):
    nr_sats = np.int32(data[0])
    
    low = int(1e1)
    high = int(1e12)
    rng    = np.random.default_rng()
    sat_id = rng.integers(low, high, size=nr_sats)
    
    apoapsis  = np.array([np.float64(data[1])] * nr_sats)
    periapsis = np.array([np.float64(data[2])] * nr_sats)
    
    # we want sma and ecc
    sma = (apoapsis + periapsis) / 2
    sma += EARTH_SEMI_MAJOR_AXIS / 1e3
    
    ecc = (apoapsis - periapsis) / (apoapsis + periapsis)
    
    raan      = np.array([np.deg2rad(np.float64(data[3]))] * nr_sats)
    argp      = np.array([np.deg2rad(np.float64(data[4]))] * nr_sats)
    incl_rad  = np.array([np.deg2rad(np.float64(data[5]))] * nr_sats)
    phases_rad = np.linspace(0, 2*np.pi, nr_sats, endpoint=False)
    
    config = np.vstack((sat_id,
                        raan,
                        argp,
                        incl_rad,
                        phases_rad,
                        sma * 1e3,
                        ecc))
    
    
    return config


def writeOrbitalConfiguration(filepath):  
    headers = {
        "sat_id": [],
        "raan": [],
        "argp": [],
        "incl_rad": [],
        "phases_rad": [],
        "sma": [],
        "ecc": [],
    }
    
    keys = headers.keys()
    header_text = f"Orbital headers: {', '.join(keys)}"
    
    print(header_text)
    print("-" * len(header_text))
    
    stay_in_loop = True
    while stay_in_loop:
        raw_input = input("Provide orbital configuration (comma-separated):\n")
        
        if "," in raw_input:
            data = [item.strip() for item in raw_input.split(",")]
            
            
            if not all(data) or len(data) != 6: 
                print("Data is incomplete! Exiting!")
                break
            
            configs = configurateOrbits(data)

        for (i, key) in enumerate(headers):
            for val in configs[i]:
                headers[key].append(val)
            
        
        more = input("Do you want to store more configurations? Y/N\n").upper().strip()
        
        if more not in ("Y", "N"):
            print("Invalid! Exiting!")
            break
        
        if more == "N":
            stay_in_loop = False
    
    # hdf5
    num_entries = len(headers["sat_id"])
    with h5py.File(f"{filepath}.hdf5", "w") as f:
        dset = f.create_dataset('orbitalConfigs', (7, num_entries), dtype=np.float64)
        dset.attrs["headers"] = list(headers.keys())
        data_to_write         = np.array([headers[key] for key in headers.keys()], dtype=np.float64)
        dset[:] = data_to_write



if __name__=="__main__":
    print('''
          -------------------------------------------------------------
          Helper-script for writing orbital configurations
          -------------------------------------------------------------
          One orbital configuration consists of 6 input parameters:
          n_sat --> nr of satellites
          apoapsis --> farthest point from central mass in an elliptical orbit  (km)
          periapsis --> closest point from central mass in an elliptical orbit (km)
          rightAscensionOfAscendingNode --> angle between the Vernal equinox and the ascending node (deg)
          argOfPerigee --> angle between the ascending node and the periapsis (deg)
          inclinationAngle --> angle of the orbital plane with the reference equatorial plane (deg)
          ''')
    
    
    path     = os.getcwd()
    
    
    parser = argparse.ArgumentParser(description="Save orbital configurations.")
    parser.add_argument("--filename", type=str, required=True, help="Name of data file")
    
    args = parser.parse_args()
    
    
    filepath = os.path.join(path,args.filename)
    writeOrbitalConfiguration(filepath)
