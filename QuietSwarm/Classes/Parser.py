from urllib.parse import ParseResult, urlencode, urlunparse


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
        
        self.server           = self.base + "/" + self.name
        
        if api_key is not None:
            self.api_key = api_key
        
    
    def _queryParameters(self, **kwargs):
        '''
        Need to assert that the following parameters 
        returned from this function match the
        web path defined through the parser object
        '''
        
        self.parameters = kwargs
        
        return self.parameters
    
    
    def _url(self,**kwargs):
        
        if not hasattr(self, "parameters") and \
                (kwargs.get('value', 0) != 0):
            
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
    
    
    def _cache(self,):
        pass
    
    
    def _clear_cache(self,):
        pass
    
        
        
            
    
    
    
        
