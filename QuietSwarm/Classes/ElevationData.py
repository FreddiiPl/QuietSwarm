from QuietSwarm.Classes.Parser import Parser
from pathlib import Path
from tqdm import tqdm
import requests


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
                api_key=None,
                ):
        
        self.scheme = self.SCHEME
        self.netlocation = self.NETLOCATION
        self.base = self.BASE
        self.name = self.NAME[dataserver]
 
        super().__init__(
                    scheme=self.SCHEME,
                    netlocation=self.NETLOCATION,
                    base=self.BASE,
                    name=self.name,
                    api_key=api_key,
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
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print("HTTP Error:", e)
                print("Response text:", response.text[:1000])

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

  
        
        