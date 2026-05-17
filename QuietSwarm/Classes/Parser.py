from urllib.parse import ParseResult, urlencode, urlunparse
from pathlib import Path
import os
import requests

class Parser:
    """
    A URL parser for handling API server endpoints and query parameters.

    Inspired by the architecture of the bmi-topography project:
    https://github.com/csdms/bmi-topography/
    """
    
    
    def __init__(
        self,
        scheme      = None,
        netlocation = None,
        base        = None,
        name        = None,
        api_key     = None
    ):
        self.scheme           = scheme
        self.netlocation      = netlocation
        self.base             = base
        self.name             = name
        
        self.server = None
        if self.base is not None and self.name is not None:
            self.server = self.base + "/" + self.name
            

        # self.url              = self._url()
        # self.query            = getattr(self, "parameters", None)
        
        if api_key is not None:
            self.api_key = api_key
            
        
    
    def _queryParameters(self, **kwargs):
        '''
        Need to assert that the following parameters 
        returned from this function match the
        web path defined through the parser object
        '''
        
        self.parameters = kwargs.copy()
        
        if self.api_key:
            self.parameters["API_Key"] = self.api_key
        
        return self.parameters
    
    
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
    
    
    def _cache(self,dir=None):
        if dir is None:
            dir = os.environ.get("CACHE_DIR", "./cache_directory")
            
        
        self.cache_dir = Path(dir).expanduser().resolve().absolute()
        
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    
    def _clear_cache(self,):
        for file in list(self.cache_dir.iterdir()):
            if file.is_file():
                try:
                    file.unlink()
                    print(f"rm {file}")
                except OSError as e:
                    print(f"Could not delete {file}: {e}")
    
    
    def download(self,filename: Path):
        
        self._url()
        self._cache()
        
        
        if filename.is_file():
            try:
                response = requests.get(self.url, stream=True)
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                response = None
            
        
        with filename.open("wb") as f:
            for chunk in response.iter_content(chunk_size=None):
                f.write(chunk)
        
        
        return filename.absolute()
        
        
        
        
            
    
    
    
        
