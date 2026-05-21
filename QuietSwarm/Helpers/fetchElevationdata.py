from QuietSwarm.Classes.ElevationData import OpenTopography
import rasterio


def fetchOpenTopographyData(south,
                            north,
                            west,
                            east,
                            api_key):
    
    
    demtype      = "COP30"
    outputFormat = "GTiff"
    dataserver   = "global"
    
    
    
    topography = OpenTopography(demtype,
                                south,
                                north,
                                west,
                                east,
                                outputFormat,
                                dataserver,
                                api_key)
    
    
    if topography.filepath.is_file():
        return topography.filepath

    topography.download()
    
    return topography.filepath
    
    

def fetchObserverLocation(observer: tuple, diff: float, api_key):
    longitude, latitude = observer
    
    north = latitude + diff
    south = latitude - diff
    west = longitude - diff
    east = longitude + diff
    
    
    filepath = fetchOpenTopographyData(south, north,
                                        west, east,
                                        api_key)
    
    
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