import geopandas as gpd
import pandas as pd


class GeoFabrikData:
    """
    A class that groups the different preprocessing methods used to process datasets used for the EVlution data
    pipeline from GeoFabrik OpenStreetMap:
    https://download.geofabrik.de/index.html
    """

    def __init__(self, place='Toronto'):
        self.place = place

    @staticmethod
    def open_shape_file(file_path):
        """
        Open shape file
        parameters:
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

    def get_places_gdf(self, place_file, place='Toronto'):
        """
        A function to process place shape files from GeoFabrik and filter for a particular city/area of the shapefile.
        Renames common columns to file specific prefixed ones and calculates place areas.

        parameters
        ----------
        place_file: str
            Name of the shape file to be read, must include the .shp extension
        place: str
            The particular place value (name) to be filtered into.

        returns
        -------
        a pandas DataFrame of the place geolocation data.
        """
        places = self.open_shape_file('Data/' + place_file)

        # To calculate scalars and other geometry, convert the coordinate reference system.
        places = places.to_crs('+proj=cea')
        places['place_area'] = places.area
        places['place_centroid'] = places.centroid.to_crs(epsg=4326)
        places = places.rename(columns=self.rename_common_cols('place'))

        place = places.loc[places['place_name'] == place]
        return place

    def get_traffic_gdf(self, traffic_file):
        """
        A function to process traffic shape files from GeoFabrik.
        Renames common column names to file specific prefixed version and adds traffic related metrics.

        parameters
        ----------
        traffic_file: str
            Name of the shape file to be read, must include the .shp extension

        returns
        -------
        a pandas DataFrame of the traffic geolocation data.
        """
        traffic = self.open_shape_file('Data/' + traffic_file)

        # To calculate scalars and other geometry, convert the coordinate reference system.
        traffic = traffic.to_crs('+proj=cea')

        # Calculate Traffic metrics
        traffic['traffic_area'] = traffic.area
        traffic['traffic_centroid'] = traffic.centroid.to_crs(epsg=4326)
        # ordering to the get the biggest traffic zones.
        traffic = traffic.sort_values(by='traffic_area',
                                      ascending=False)

        traffic = traffic.rename(columns=self.rename_common_cols('traffic'))
        return traffic

    def get_poi_gdf(self, poi_file):
        """
        A function to process points of interest shape files from GeoFabrik.
        Renames common column names to file specific prefixed version and adds traffic related metrics.

        parameters
        ----------
        poi_file: str
            Name of the shape file to be read, must include the .shp extension

        returns
        -------
        a pandas DataFrame of the place geolocation data.
        """
        poi = self.open_shape_file('Data/' + poi_file)

        # To calculate scalars and other geometry, convert the coordinate reference system.
        poi = poi.to_crs('+proj=cea')
        poi['poi_centroids'] = poi.centroid.to_crs(epsg=4326)
        poi['poi_area'] = poi.area
        poi = poi.rename(columns=self.rename_common_cols('poi'))

        return poi

    def get_place_traffic_gdf(self, place_file_path, traffic_file_path, place='Toronto'):
        # Get the preprocessed files for place and traffic.
        place_gdf = self.get_places_gdf(place_file_path, place=place)
        traffic_gdf = self.get_traffic_gdf(traffic_file_path)

        # spatial join the two and remove unneeded data records.
        place_traffic = gpd.sjoin(place_gdf, traffic_gdf, how='inner')
        place_traffic = place_traffic.sort_values(by=['place_area', 'traffic_area'], ascending=False)
        place_traffic = place_traffic.drop_duplicates(subset=['traffic_name'])
        return place_traffic

    def get_place_poi_gdf(self, place_file_path, poi_file_path,  place='Toronto'):
        # Get the preprocessed files for place and traffic.
        place_gdf = self.get_places_gdf(place_file_path, place=place)
        poi_gdf = self.get_poi_gdf(poi_file_path)

        # spatial join the two and remove unneeded data records.
        place_poi = gpd.sjoin(place_gdf, poi_gdf, how='inner')
        place_poi = place_poi.sort_values(by=['place_area', 'poi_area'], ascending=False)
        place_poi = place_poi.drop_duplicates(subset=['poi_name'])
        return place_poi

