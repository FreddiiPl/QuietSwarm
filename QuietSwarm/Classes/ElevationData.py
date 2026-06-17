from QuietSwarm.Classes.Parser import Parser
from urllib.parse import ParseResult, urlencode, urlunparse
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
import numpy as np
import requests
import os

script_dir = Path(__file__).resolve().parent
credentials_path = script_dir / "../credentials.env"

load_dotenv(credentials_path)


class OpenTopography(Parser):
    
    SCHEME        = "https"
    NETLOCATION   = "portal.opentopography.org"
    BASE          = "API"
    
    NAME          = {"global": "globaldem", "usgs": "usgsdem"}
    VALID_FORMATS = {"GTiff": "tif", "AAIGrid": "asc", "HFA": "img"}
    
    
    def __init__(self,
                demtype=None,
                south=None,
                north=None,
                west=None,
                east=None,
                outputFormat=None,
                dataserver=None,
                ):
        
        self.demtype = demtype
        self.outputFormat = outputFormat
        self.dataserver = dataserver
        
        self.scheme = self.SCHEME
        self.netlocation = self.NETLOCATION
        self.base = self.BASE
        self.name = self.NAME[dataserver]
 
        self.api_key = os.getenv("OpenTopography_API_Key")
        super().__init__(
                    scheme=self.SCHEME,
                    netlocation=self.NETLOCATION,
                    base=self.BASE,
                    name=self.name,
                    api_key=self.api_key,
                    )
        
        
        self._cache()
        if outputFormat in self.VALID_FORMATS.keys():
            file_extension = self.VALID_FORMATS[outputFormat]
            
            self.filename = (
                f"{demtype}"
                f"_{south}"
                f"_{north}"
                f"_{west}"
                f"_{east}"
                f".{file_extension}"
            )
            
            self.filepath = Path(self.cache_dir) / self.filename
            
            self.url = self._url(demtype=demtype,
                                 south=south,
                                 north=north,
                                 west=west,
                                 east=east,
                                 outputFormat=outputFormat)
            
        
    def download(self):
        
        if not self.filepath.is_file():
            
            try:
                print("Fetching response...")
                response = requests.get(self.url, stream=True)
                
                content_type = response.headers.get("Content-Type", "")
                
                if "application/xml" in content_type or "text/xml" in content_type:
                    raise RuntimeError(response.text)
                
                response.raise_for_status()
                
            except (requests.exceptions.HTTPError, RuntimeError) as e:
                print("API Error:", e)
                raise

            total_bytes = int(response.headers.get("content-length", 0))
            # total_gb    = total_bytes / (1024 ** 3)
            chunk_size = 1024 * 1024
            
            with self.filepath.open("wb") as f:
                with tqdm(
                          total=total_bytes,
                          unit="B",
                          unit_scale=True,
                          unit_divisor=1024,
                          desc="Downloading Elevation Data"
                          ) as pbar:
                                for chunk in response.iter_content(chunk_size=chunk_size):
                                    if chunk:
                                        f.write(chunk)
                                        pbar.update(len(chunk))
        
        
        return self.filepath.absolute()
    
    
    def download_recursive(self, south, north, west, east, depth=0, max_depth=6):
        south = np.round(south, 3)
        north = np.round(north, 3)
        west = np.round(west, 3)
        east = np.round(east, 3)
        
        topo = OpenTopography(
                demtype=self.demtype,
                south=south,
                north=north,
                west=west,
                east=east,
                outputFormat=self.outputFormat,
                dataserver=self.dataserver
            )
        
        if topo.filepath.is_file():
            return [topo.filepath]

        try:
            filepath = topo.download()
            return [filepath]
        
        except Exception as e:
            msg = str(e)
            
            if "maximum area" not in msg.lower():
                raise

            if depth >= max_depth:
                print("Max recursion depth reached, skipping",
                        south, north, west, east)
                return []
            
            print(f"Splitting tile at depth {depth}")
            
            
            mid_lat = (south + north) / 2
            mid_lon = (west + east) / 2

            tiles = [
                (south, mid_lat, west, mid_lon),
                (south, mid_lat, mid_lon, east),
                (mid_lat, north, west, mid_lon),
                (mid_lat, north, mid_lon, east),
            ]


            results = []
            for s, n, w, e in tiles:
                results.extend(self.download_recursive(s, n, w, e, depth+1, max_depth))
            
            print("Finished!")
            return results

        else:
            raise
            
            
    def _url(self,**kwargs):
        if not hasattr(self, "parameters") and kwargs:
                self.parameters = self._queryParameters(**kwargs)
        
        
        components = ParseResult(
            scheme=self.scheme,
            netloc=self.netlocation,
            path=self.server,
            params="",
            query=urlencode(self.parameters),
            fragment=""
        )
        
        return urlunparse(components)
  
    
  
  
class Lantmateriet(Parser):
        
    SCHEME        = "https"
    NETLOCATION   = "api.lantmateriet.se"
    DATASERVER    = "stac-hojd/v1"
    
    
    def __init__(self,
                 south=None,
                 north=None,
                 west=None,
                 east=None,
                 collection="hojddata2"):
        
        self.scheme = self.SCHEME
        self.netlocation = self.NETLOCATION
        self.base = self.DATASERVER
        
        super().__init__(
                    scheme=self.SCHEME,
                    netlocation=self.NETLOCATION,
                    base=self.DATASERVER,
                    )
        
        
        self.south = south
        self.north = north
        self.west = west
        self.east = east
        self.collection = collection
        
        self._cache()
    
    
    def search(self):
        body = self._search_body()
        url = self._url("search")
        return requests.post(url, json=body).json()
    
    
    def assets(self):
        result = self.search()
        for feature in result["features"]:
            yield feature["assets"]["data"]["href"]
    
    
    def download_all(self):
        for href in self.assets():
            filename = href.split("/")[-1]
            filepath = Path(self.cache_dir) / filename

            if not filepath.exists():
                r = requests.get(href, stream=True)
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(1024 * 1024):
                        f.write(chunk)

            yield filepath
    
    
    def _url(self, *parts):
        path = "/".join([self.base] + list(parts))
        components = ParseResult(
            scheme=self.scheme,
            netloc=self.netlocation,
            path=path,
            params="",
            query="",
            fragment=""
        )
        return urlunparse(components)
        
        
    def _search_body(self):
        return {
            "bbox": [self.west, self.south, self.east, self.north],
            "collections": [self.collection],
            "limit": 100
        }  
            