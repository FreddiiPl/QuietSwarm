from QuietSwarm.Classes.Parser import Parser
from pathlib import Path


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
            
        
    def download(self):
        pass

  
        
        