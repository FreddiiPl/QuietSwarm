import pandas as pd
import re

def main():
    pathname = PATHNAME
    
    rows = []
    current_j = None
    
    with open(pathname, "r") as file:
        for line in file:
            line = line.strip()
            
            
            m = re.match(r"j\s*=\s*(\d+)", line)
            if m:
                current_j = int(m.group(1))
                continue
                
            if not line or "Number of terms" in line:
                continue
        
            parts = list(map(float, line.split()))
            rows.append([current_j] + parts)
    
    
    cols = ["j", "index", "val1", "val2"] + [f"c{i}" for i in range(1, len(rows[0]) - 3)]
    df = pd.DataFrame(rows, columns=cols)
    
    tab5_2b_j = df[df["j"] == 4]
    
    tab5_2b_j.to_csv("tab5.2b.j4.csv", index=False)

if __name__ == "__main__":
    main()