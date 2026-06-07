import rasterio
import matplotlib.pyplot as plt
import numpy as np


def main():
    path = "/home/fredpl/Projekt/QuietSwarm/testing/cache_directory/COP30_59.305896_59.505896_18.072604_18.272604.tif"
    
    with rasterio.open(path) as src:
        data = src.read(1)
        
        extent = [
            src.bounds.left,
            src.bounds.right,
            src.bounds.bottom,
            src.bounds.top
        ]
        
    cm = plt.get_cmap("turbo")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title("Elevation Map", fontweight="bold")
    ax.imshow(data, extent=extent, cmap=cm)
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    
    plt.colorbar(ax.imshow(data, extent=extent, cmap=cm), ax=ax, label="Elevation (m)")
    plt.tight_layout()
    plt.savefig("elevation_map.png", dpi=300)

if __name__ == "__main__":
    main()