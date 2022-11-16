import geopandas as gpd
import pandas as pd
from preprocess_data.calcs import lat_to_km, lng_to_km
from preprocess_data.s3_connect import EVlutionS3Input


class GeoLocData:
    """
    A class that groups the different preprocessing methods used to process datasets used for the EVlution data
    pipeline from GeoFabrik OpenStreetMap and public charging stations dataset:
    https://download.geofabrik.de/index.html
    """

    def __init__(self, s3=False):
        self.charging_stations = None
        self.places = None
        self.traffic = None
        self.poi = None
        self.s3 = s3
        if self.s3:
            self.s3_data = EVlutionS3Input()

    @staticmethod
    def open_shape_file(file_path):
        """
        OpenStreetMap shape file

        parameters:
        -----------
            file_path: the full path to the shape file to be opened with extension .shp
        """
        return gpd.read_file(file_path)

    @staticmethod
    def rename_common_cols(prefix):
        """
        A simple function to rename common GeoFabrik file columns to prefix with the type of file.
        e.g. 'name': 'place_name'
        """
        rename_dict = {
            'osm_id': prefix + '_osm_id',
            'code': prefix + '_code',
            'fclass': prefix + '_fclass',
            'name': prefix + '_name'
        }
        return rename_dict

    def get_charging_stations_data(
                                   self,
                                   city=None,
                                   file_path='preprocess_data/Data/Ontario_Electric_Charging_Stations.csv',
                                  ):
        """
        Ontario Public Charging Stations csv file

        parameters:
        -----------
            city: str, None
                If filtering the charging stations dataset to a particular city, insert the name of the city as
                provided in the data.
            s3: bool
                If True, access the data through S3 bucket. If false, then use the file_path argument provided to read
                the data from a local file path.
            file_path: str
                The full path to the charging stations data stored in a local folder.

        returns
        -------
        A pandas DataFrame of the Ontario Electric Charging Stations Data with preprocessing steps applied.
        """
        if self.s3:
            charging_stations = self.s3_data.get_charging_stations_data_raw()
        else:
            charging_stations = pd.read_csv(file_path)

        cols = [
            'X',
            'Y',
            'Fuel_Type_Code',
            'Station_Name',
            'Street_Address',
            'Intersection_Directions',
            'City',
            'State',
            'ZIP',
            'Status_Code',
            'Expected_Date',
            'Groups_With_Access_Code',
            'Access_Days_Time',
            'Date_Last_Confirmed'
        ]
        charging_stations = charging_stations[cols]
        charging_stations = gpd.GeoDataFrame(charging_stations,
                                             geometry=gpd.points_from_xy(charging_stations.X,
                                                                         charging_stations.Y),
                                             crs='EPSG:4326'
                                             )
        # field containing lat and lng to km.
        charging_stations['x_km'] = charging_stations.X.apply(lambda x: lng_to_km(x))
        charging_stations['y_km'] = charging_stations.Y.apply(lambda y: lat_to_km(y))

        # renaming for standardising column names.
        charging_stations = charging_stations.rename(columns={'X': 'x',
                                                              'Y': 'y'})

        # filtering for places depending on input type.
        if isinstance(city, type(None)):
            charging_stations = charging_stations
        elif isinstance(city, (list, tuple, set, pd.Series)):
            charging_stations = charging_stations[charging_stations['City'].isin(city)]
            charging_stations = charging_stations
        else:
            charging_stations = charging_stations.loc[charging_stations['City'] == city]
            charging_stations = charging_stations

        self.charging_stations = charging_stations

    def get_places_gdf(
                       self,
                       place=None,
                       place_file='preprocess_data/Data/gis_osm_places_a_free_1.shp'
                      ):
        """
        A function to process place shape files from GeoFabrik and filter for a particular city/area of the shapefile.
        It will also incorporate the stage at which the charging stations data is brougth in.
        Renames common columns to file specific prefixed ones and calculates place areas.

        parameters
        ----------
        place: str, List[str], None
            The particular place values (names) to be filtered into. Can be None or an iterable with a list of places.
        s3: bool
            If True, access the data through S3 bucket. If false, then use the file_path argument provided to read
            the data from a local file path.
        place_file: str
            Name of the shape file to be read, must include the .shp extension
        returns
        -------
        a pandas DataFrame of the place geolocation data.
        """

        if self.s3:
            places = self.s3_data.get_places_data_raw()
        else:
            places = self.open_shape_file(place_file)

        places = places.rename(columns=self.rename_common_cols('place'))

        # filtering for places depending on the filter of place.
        if isinstance(place, type(None)):
            places = places
        elif isinstance(place, (list, tuple, set, pd.Series)):
            places = places[places['place_name'].isin(place)]
            places = places
        else:
            places = places.loc[places['place_name'] == place]
            places = places

        # To calculate scalars and other geometry, convert the coordinate reference system.
        places = places.to_crs('+proj=cea')
        places['place_area'] = places.area
        places['place_centroid'] = places.centroid.to_crs(epsg=4326)

        places['place_x'] = places.place_centroid.x
        places['place_y'] = places.place_centroid.y

        # field containing lat and lng to km.
        places['place_x_km'] = places.place_x.apply(lambda x: lng_to_km(x))
        places['place_y_km'] = places.place_y.apply(lambda y: lat_to_km(y))

        self.places = places

    def get_traffic_gdf(
                        self,
                        traffic_file='preprocess_data/Data/gis_osm_traffic_a_free_1.shp'
                        ):
        """
        A function to process traffic shape files from GeoFabrik.
        Renames common column names to file specific prefixed version and adds traffic related metrics.

        parameters
        ----------
        s3: bool
            If True, access the data through S3 bucket. If false, then use the file_path argument provided to read
            the data from a local file path.
        traffic_file: str
            Name of the shape file to be read, must include the .shp extension

        returns
        -------
        a geopandas DataFrame of the traffic geolocation data.
        """
        if self.s3:
            traffic = self.s3_data.get_traffic_data_raw()
        else:
            traffic = self.open_shape_file(traffic_file)

        traffic = traffic.rename(columns=self.rename_common_cols('traffic'))

        # To calculate scalars and other geometry, convert the coordinate reference system.
        traffic = traffic.to_crs('+proj=cea')

        # Calculate Traffic metrics
        traffic['traffic_area'] = traffic.area
        traffic['traffic_centroid'] = traffic.centroid.to_crs(epsg=4326)
        # ordering to the get the biggest traffic zones.
        traffic = traffic.sort_values(by='traffic_area',
                                      ascending=False)

        # storing coordinates x and y in separate columns as well as converting degrees to km.
        traffic['traffic_x'] = traffic.traffic_centroid.x
        traffic['traffic_y'] = traffic.traffic_centroid.y

        traffic['traffic_x_km'] = traffic.traffic_x.apply(lambda x: lng_to_km(x))
        traffic['traffic_y_km'] = traffic.traffic_y.apply(lambda y: lat_to_km(y))
        self.traffic = traffic

    def get_poi_gdf(
                    self,
                    poi_file='preprocess_data/Data/gis_osm_pois_a_free_1.shp'
                    ):
        """
        A function to process points of interest shape files from GeoFabrik.
        Renames common column names to file specific prefixed version and adds traffic related metrics.

        parameters
        ----------
        s3: bool
            If True, access the data through S3 bucket. If false, then use the file_path argument provided to read
            the data from a local file path.
        poi_file: str
            Name of the shape file to be read, must include the .shp extension

        returns
        -------
        a geopandas DataFrame of the place of interest geolocation data.
        """
        if self.s3:
            poi = self.s3_data.get_poi_data_raw()
        else:
            poi = self.open_shape_file(poi_file)

        poi = poi.rename(columns=self.rename_common_cols('poi'))

        # To calculate scalars and other geometry, convert the coordinate reference system.
        poi = poi.to_crs('+proj=cea')
        poi['poi_centroids'] = poi.centroid.to_crs(epsg=4326)
        poi['poi_area'] = poi.area

        # storing coordinates x and y in separate columns as well as converting degrees to km.
        poi['poi_x'] = poi.poi_centroids.x
        poi['poi_y'] = poi.poi_centroids.y

        poi['poi_x_km'] = poi.poi_x.apply(lambda x: lng_to_km(x))
        poi['poi_y_km'] = poi.poi_y.apply(lambda y: lat_to_km(y))

        self.poi = poi

    def get_place_traffic_gdf(
                              self,
                              place=None
                            ):
        # Get the preprocessed files for place and traffic.
        self.get_places_gdf(place=place)
        self.get_traffic_gdf()

        place_gdf = self.places
        traffic_gdf = self.traffic

        # spatial join the two and remove unneeded data records.
        place_traffic = gpd.sjoin(place_gdf, traffic_gdf, how='inner')
        place_traffic = place_traffic.sort_values(by=['place_area', 'traffic_area'], ascending=False)
        place_traffic = place_traffic.drop_duplicates(subset=['traffic_name'])

        place_traffic = place_traffic.drop(labels=['index_right', 'index_left'],
                                           errors='ignore')

        return place_traffic

    def get_place_poi_gdf(self, place=None):
        # Get the preprocessed files for place and traffic.
        self.get_places_gdf(place=place)
        self.get_poi_gdf()

        place_gdf = self.places
        poi_gdf = self.poi

        # spatial join the two and remove unneeded data records.
        place_poi = gpd.sjoin(place_gdf, poi_gdf, how='inner')
        place_poi = place_poi.sort_values(by=['place_area', 'poi_area'], ascending=False)
        place_poi = place_poi.drop_duplicates(subset=['poi_name'])

        place_poi = place_poi.drop(labels=['index_right', 'index_left'],
                                   errors='ignore')

        return place_poi
