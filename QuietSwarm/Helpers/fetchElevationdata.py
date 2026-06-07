from QuietSwarm.Classes.ElevationData import OpenTopography
from rasterio.merge import merge
import rasterio
from rasterio.io import MemoryFile


def split_bbox(south, north, west, east, max_deg=1.0):
    """
    Splits a bounding box into smaller tiles.
    max_deg controls tile size in degrees.
    """

    lat_steps = int((north - south) / max_deg) + 1
    lon_steps = int((east - west) / max_deg) + 1

    lat_edges = [
        south + i * max_deg
        for i in range(lat_steps)
    ] + [north]

    lon_edges = [
        west + i * max_deg
        for i in range(lon_steps)
    ] + [east]

    tiles = []

    for i in range(len(lat_edges) - 1):
        for j in range(len(lon_edges) - 1):
            tiles.append((
                lat_edges[i],
                lat_edges[i + 1],
                lon_edges[j],
                lon_edges[j + 1],
            ))

    return tiles


def fetch_tiled_opentopo(south, north, west, east, max_deg=1.0):
    tiles = split_bbox(south, north, west, east, max_deg=max_deg)

    datasets = []

    for s, n, w, e in tiles:
        path = fetchOpenTopographyData(s, n, w, e)

        with rasterio.open(path) as src:
            data = src.read(1)
            transform = src.transform

            datasets.append((data, transform, src.bounds))

    return datasets


def merge_tiles(tile_paths):
    srcs = [rasterio.open(p) for p in tile_paths]

    mosaic, transform = merge(srcs)

    for s in srcs:
        s.close()

    return mosaic[0], transform


def fetchOpenTopographyData(south,
                            north,
                            west,
                            east):
    
    
    demtype      = "COP30"
    outputFormat = "GTiff"
    dataserver   = "global"
    
    topography = OpenTopography(demtype,
                                south,
                                north,
                                west,
                                east,
                                outputFormat,
                                dataserver)
    
    
    if topography.filepath.is_file():
        return topography.filepath

    topography.download()
    
    return topography.filepath
    
    

def fetchObserverLocation(observer: tuple, diff: float):
    longitude, latitude = observer
    
    north = latitude + diff
    south = latitude - diff
    west  = longitude - diff
    east  = longitude + diff
    

    filepath = fetchOpenTopographyData(south, north,
                                        west, east)
    
    
    with rasterio.open(filepath) as src:
        data = src.read(1)
        
        extent = [
            src.bounds.left,
            src.bounds.right,
            src.bounds.bottom,
            src.bounds.top
        ]
        
    
    center_row = data.shape[0] // 2
    center_col = data.shape[1] // 2
    
    height = data[center_row, center_col]
    
    return (data, extent), (longitude, latitude, height)
        
    



def multipleFetchTopographyData(bounding_box):
    pass