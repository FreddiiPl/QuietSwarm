from urllib.parse import ParseResult, urlencode, urlunparse
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
import numpy as np
import requests
import os

import geopandas as gpd
from shapely import points
import rasterio

script_dir = Path(__file__).resolve().parent
credentials_path = script_dir / "../credentials.env"

load_dotenv(credentials_path)

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
 
        
        if api_key is not None:
            self.api_key = api_key
            
        
    
    def _queryParameters(self, **kwargs):
        '''
        Need to assert that the following parameters 
        returned from this function match the
        web path defined through the parser object
        '''
        
        self.parameters = kwargs.copy()
        
        if hasattr(self, "api_key"):
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




class TerrestrialGrid:
    data_path = script_dir / "../Files/CNTR_RG_01M_2024_4326.gpkg"
    
    viable_countries = ['Gambia', 'Guam', 'Guinea-Bissau', 'Essequibo', 'Hong Kong', 'Heard Island and Mcdonald Islands', 'Honduras', 'Croatia', 'Haiti', 'Hungary', 'Indonesia',
 'Ireland', 'Andorra', 'United Arab Emirates', 'Afghanistan', 'Antigua and Barbuda', 'Anguilla', 'Albania', 'Armenia', 'Angola', 'Antarctica', 'Argentina',
 'American Samoa', 'Austria', 'Australia', 'Aruba', 'Azerbaijan', 'Bosnia and Herzegovina', 'Barbados', 'Bangladesh', 'Belgium', 'Burkina Faso', 'Bulgaria', 
 'Bahrain', 'Burundi', 'Benin', 'Saint Barthélemy', 'Bermuda', 'Brunei', 'Bolivia', 'Bonaire, Sint Eustatius and Saba', 'Brazil', 'Bahamas', 'Bhutan', 
 'Bouvet Island', 'Botswana', 'Belarus', 'Canada', 'Cocos (Keeling) Islands', 'Democratic Republic of The Congo', 'Central African Republic', 'Congo',
 'Switzerland', 'Côte D’Ivoire', 'Cook Islands', 'Chile', 'Cameroon', 'China', 'Colombia', 'Clipperton Island', 'Costa Rica', 'Cuba', 'Cape Verde', 
 'Curaçao', 'Christmas Island', 'Cyprus', 'Czechia', 'Germany', 'Djibouti', 'Denmark', 'Dominica', 'Dominican Republic', 'Algeria', 'Ecuador', 'Estonia', 
 'Egypt', 'Western Sahara', 'Greece', 'Eritrea', 'Spain', 'Ethiopia', 'Finland', 'Fiji', 'Falkland Islands', 'Micronesia', 'Faroes', 'France', 'Gabon',
 'Grenada', 'Georgia', 'Guernsey', 'Ghana', 'Gibraltar', 'Greenland', 'Guinea', 'Equatorial Guinea', 'South Georgia and The South Sandwich Islands',
 'Guatemala', 'Tuvalu', 'United Republic of Tanzania', 'Ukraine', 'Uganda', 'United Kingdom', 'United States Minor Outlying Islands', 'United States',
 'Uruguay', 'Uzbekistan', 'Vatican City', 'Israel', 'Isle of Man', 'India', 'Iraq', 'Iran', 'Iceland', 'Italy', 'Jersey', 'Jamaica', 'Jordan', 'Kenya',
 'Kyrgyzstan', 'Cambodia', 'Kiribati', 'Comoros', 'Saint Kitts and Nevis', 'North Korea', 'Kuwait', 'Cayman Islands', 'Kazakhstan', 'Laos', 'Lebanon',
 'Saint Lucia', 'Liechtenstein', 'Sri Lanka', 'Liberia', 'Lesotho', 'Lithuania', 'Luxembourg', 'Latvia', 'Libya', 'Morocco', 'Monaco', 'Moldova',
 'Montenegro', 'Madagascar', 'Marshall Islands', 'North Macedonia', 'Mali', 'Myanmar/Burma', 'Mongolia', 'Macau', 'Northern Mariana Islands', 'Mauritania',
 'Montserrat', 'Malta', 'Mauritius', 'Maldives', 'Malawi', 'Mexico', 'Malaysia', 'Mozambique', 'Namibia', 'New Caledonia', 'Niger', 'Norfolk Island', 'Nigeria',
 'Nicaragua', 'Netherlands', 'Norway', 'Nepal', 'Nauru', 'Niue', 'New Zealand', 'Oman', 'Panama', 'Peru', 'French Polynesia', 'Papua New Guinea', 'Philippines',
 'Pakistan', 'Poland', 'Saint Pierre and Miquelon', 'Pitcairn Islands', 'Puerto Rico', 'Palestine', 'Portugal', 'Palau', 'Paraguay', 'Qatar', 'Romania',
 'Serbia', 'Russian Federation', 'Rwanda', 'Saudi Arabia', 'Solomon Islands', 'Seychelles', 'Sudan', 'Sweden', 'Singapore',
 'Saint Helena, Ascension and Tristan Da Cunha', 'Slovenia', 'Svalbard and Jan Mayen', 'Slovakia', 'Sierra Leone', 'San Marino', 'Senegal',
 'Somalia', 'Suriname', 'South Sudan', 'São Tomé and Príncipe', 'El Salvador', 'Sint-Maarten', 'Syria', 'Eswatini', 'Turks and Caicos Islands',
 'Chad', 'French Southern and Antarctic Lands', 'Togo', 'Thailand', 'Tajikistan', 'Tokelau', 'Timor-Leste', 'Turkmenistan', 'Tunisia', 'Tonga', 'Türkiye',
 'Trinidad and Tobago', 'Japan', 'Saint Vincent and The Grenadines', 'Venezuela', 'British Virgin Islands', 'Us Virgin Islands', 'Viet nam', 'Vanuatu',
 'Wallis and Futuna', 'Samoa', 'Paracel Islands', 'Spratly Islands', 'Aksai Chin', 'Arunachal Pradesh', 'China/India', 'Jammu Kashmir', 'Kuril Islands',
 'No mans land', 'Navassa Island', 'Scarborough Reef', 'Senkaku Islands', 'Bassas Da India', 'Abyei', 'Bir Tawil (Disputed Territory)',
 'Equatorial Guinea/Gabon (disputed territory) ', 'Chagos Islands (disputed territory)', 'Yemen', 'South Africa', 'Zambia', 'Zimbabwe', 'South Korea',
 'Liancourt Rock', 'Ilemi Triangle', 'Belize', 'Guyana', 'Sapodilla Cayes', 'Belize/Guatemala', "Hala'Ib Triangle"] 
    
    def __init__(self,
                 country):
        
        gdf = gpd.read_file(self.data_path)
        
        matches = [b for b in self.viable_countries if country.lower() == b.lower()]
        if not matches:
            raise ValueError(f"{country} is not a viable query name!")
        
        self.country = matches[0]
        
        self.border_data = gdf[gdf["NAME_ENGL"] == self.country]
    
    
    def get_total_bounds(self, data=None, EPSG="EPSG:3035"):
        
        if data is None:
            data = self.border_data
        
        curr_data = data.to_crs(EPSG)
        minx, miny, maxx, maxy = curr_data.total_bounds
        
        return (minx, miny, maxx, maxy)
    
    
    def generate_gridpoints(self,nr_points, bounds=None):
        if bounds is None:
            bounds = self.get_total_bounds()
        
        minx, miny, maxx, maxy = bounds
        
        x_coords = np.linspace(minx, maxx, nr_points)
        y_coords = np.linspace(miny, maxy, nr_points)
        
        xx, yy = np.meshgrid(x_coords, y_coords)
        grid_pts =  points(xx.ravel(), yy.ravel())
        
        grid = gpd.GeoDataFrame(geometry=grid_pts, crs="EPSG:3035")
        grid = gpd.sjoin(grid, self.border_data.to_crs(grid.crs), predicate="within")
        return grid

    
    def fetch_dem_heights(self, data, demtype="COP30", outputFormat="GTiff", dataserver="global"):
        minx, miny, maxx, maxy = self.get_total_bounds(data, EPSG="EPSG:4326")
        
        self.topo = OpenTopography(demtype=demtype,
                              south=miny,
                              north=maxy,
                              west=minx,
                              east=maxx,
                              outputFormat=outputFormat,
                              dataserver=dataserver)
        
        filepaths = self.topo.download_recursive(south=miny,
                                            north=maxy,
                                            west=minx,
                                            east=maxx)
        
        grid  = self.construct_heights(filepaths, data)
        
        return grid
        
        
    def construct_heights(self, filepaths, grid):
            
            new_grid = grid.to_crs("EPSG:4326").copy()
            lons = new_grid.geometry.x.values
            lats = new_grid.geometry.y.values
            
            heights = np.full(len(new_grid), np.nan)
            
            for filepath in filepaths:
                nans_mask = np.isnan(heights)
                if not np.any(nans_mask):
                    break
                
                with rasterio.open(filepath) as src:
                    rows, cols = rasterio.transform.rowcol(src.transform, lons, lats)
                    rows = np.array(rows)
                    cols = np.array(cols)

                    valid_idx = (
                        (rows >= 0) & (rows < src.height) & 
                        (cols >= 0) & (cols < src.width) & 
                        nans_mask
                    )
                    
                    if not np.any(valid_idx):
                        continue
                    
                    band_data = src.read(1)
                    pixel_vals = band_data[rows[valid_idx], cols[valid_idx]]
                    
                    if src.nodata is not None:
                        is_valid_val = pixel_vals != src.nodata
                        final_idx = np.where(valid_idx)[0][is_valid_val]
                        heights[final_idx] = pixel_vals[is_valid_val]
                    else:
                        heights[valid_idx] = pixel_vals
                
            new_grid["height"] = heights
                    
            return new_grid
            
            
        
    
         
        
    
    
        
        
