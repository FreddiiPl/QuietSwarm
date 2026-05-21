import rasterio
import matplotlib.pyplot as plt


def main():
    path = "..."
    
    with rasterio.open(path) as src:
        data = src.read(1)
        
        extent = [
            src.bounds.left,
            src.bounds.right,
            src.bounds.bottom,
            src.bounds.top
        ]
        
    
    plt.figure(figsize=(12,8))
    plt.imshow(data, extent=extent, cmap="terrain")
    plt.colorbar(label="Elevation")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.show()

if __name__ == "__main__":
    main()