from QuietSwarm.Classes.ElevationData import OpenTopography
import geopandas as gpd
import numpy as np
import rasterio
from shapely import points

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



def main():
    file = "CNTR_RG_01M_2024_4326.gpkg"
    gdf  = gpd.read_file(file)

    cntry_name = "Schweden"
    gdf_cntry  = gdf[gdf['NAME_GERM'] == cntry_name].copy()
    gdf_cntry  = gdf_cntry.to_crs("EPSG:3035")
    
    nr_points = 1000
    min_x, min_y, max_x, max_y = gdf_cntry.total_bounds

    x_coords = np.linspace(min_x, max_x, nr_points)
    y_coords = np.linspace(min_y, max_y, nr_points)

    xx, yy   = np.meshgrid(x_coords, y_coords)
    grid_pts = points(xx.ravel(), yy.ravel())
    
    grid          = gpd.GeoDataFrame(geometry=grid_pts, crs=gdf_cntry.crs)
    grid_in_cntry = gpd.sjoin(grid, gdf_cntry, predicate='within')
    grid_in_cntry = grid_in_cntry.to_crs("EPSG:4326")
    
    
    min_x, min_y, max_x, max_y = grid_in_cntry.total_bounds

    demtype = "COP30"
    outputFormat = "GTiff"
    dataserver = "global"


    topo = OpenTopography(demtype=demtype,
                        south=min_y,
                        north=max_y,
                        west=min_x,
                        east=max_x,
                        outputFormat=outputFormat,
                        dataserver=dataserver)


    filepaths = topo.download_recursive(south=min_y,
                                        north=max_y,
                                        west=min_x,
                                        east=max_x)
    
    
    grid_in_cntry["height"] = np.nan
    coords                  = [(pt.x, pt.y) for pt in grid_in_cntry.geometry]
    heights                 = np.full(len(coords), np.nan)

    for filepath in filepaths:
        with rasterio.open(filepath) as src:
            bounds = src.bounds
            
            for i, (lon, lat) in enumerate(coords):
                if np.isnan(heights[i]):
                    if not (
                        bounds.left <= lon <= bounds.right and
                        bounds.bottom <= lat <= bounds.top
                    ):
                        continue
                    
                    val = list(src.sample([(lon, lat)]))[0][0]
                    
                    
                    if src.nodata is None or val != src.nodata:
                        
                        heights[i] = val
        
    grid_in_cntry["height"] = heights
    
    lon, lat = grid_in_cntry["geometry"].x, grid_in_cntry["geometry"].y
    height   = grid_in_cntry["height"]
    
    fig, ax = plt.subplots(figsize=(12,8))
    ax.scatter(lon, lat, c=height, s=20, cmap="terrain")

    plt.axis("equal")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()