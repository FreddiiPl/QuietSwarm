import os
import argparse

def writeOrbitalConfiguration(filepath):  
    headers = {
        "nr_sat": [],
        "apoapsis": [],
        "periapsis": [],
        "rightAscensionOfAscendingNode": [],
        "argumentOfPerigee": [],
        "inclinationAngle": [],
        "phaseSeparation": []
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
            
            
            if not all(data) or len(data) != len(keys): 
                print("Data is incomplete! Exiting!")
                break
            
        
        for (i, key) in enumerate(keys):
            headers[key].append(data[i])
            
        
        more = input("Do you want to store more configurations? Y/N\n").upper().strip()
        
        if more not in ("Y", "N"):
            print("Invalid! Exiting!")
            break
        
        if more == "N":
            stay_in_loop = False
    
    
    file_text = ",".join(headers.keys())
    with open(filepath, "w") as f:
        
        f.write(",".join(headers.keys()) + "\n")
        
        num_entries = len(headers["nr_sat"])
        
        for i in range(num_entries):
            row = [headers[key][i] for key in headers.keys()]
            f.write(",".join(row) + "\n")



if __name__=="__main__":
    print('''
          -------------------------------------------------------------
          Helper-script for writing orbital configurations
          -------------------------------------------------------------
          One orbital configuration consists of 7 input parameters:
          n_sat --> nr of satellites
          apoapsis --> farthest point from central mass in an elliptical orbit 
          periapsis --> closest point from central mass in an elliptical orbit
          rightAscensionOfAscendingNode --> angle between the Vernal equinox and the ascending node
          argOfPerigee --> angle between the ascending node and the periapsis
          inclinationAngle --> angle of the orbital plane with the reference equatorial plane
          phaseSeparation --> separation between objects in the orbital plane
          ''')
    
    
    path     = os.getcwd()
    
    
    parser = argparse.ArgumentParser(description="Spara orbital-konfigurationer.")
    parser.add_argument("--filename", type=str, required=True, help="Namnet på filen som ska skrivas")
    
    args = parser.parse_args()
    
    
    filepath = os.path.join(path,args.filename)
    writeOrbitalConfiguration(filepath)