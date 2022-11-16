from boto3 import resource
import geopandas as gpd
import pandas as pd
from decouple import config


class EVlutionS3Input:

    def __init__(self):
        self.aws_region_name = config('EVLUTION_AWS_REGION_NAME')
        self.aws_access_key_id = config('EVLUTION_AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = config('EVLUTION_AWS_SECRET_ACCESS_KEY')
        self.bucket_name = config('EVLUTION_BUCKET_NAME')

    @staticmethod
    def pdf_to_gdf(df: pd.DataFrame, geo_col: str = 'geometry'):
        """
        A function to convert a pandas DataFrame to a GeoDataFrame with a geomtery column

        parameters
        ----------
        df: pandas DataFrame
            A pandas DataFrame to be converted to a geoDataFrame.
        geo_col: str
            The column in the pandas DataFrame to be assigned the geo series in teh GeoDataFrame.
        """
        gs = gpd.GeoSeries.from_wkt(df[geo_col])
        gdf = gpd.GeoDataFrame(df,
                               geometry=gs,
                               crs='EPSG:4326')
        return gdf

    def access_evlution_input_s3(self):
        """
        Put in user credentials to access s3 data source.
        This needs to be configured to run programmatically for each user who uses the repo in their local environment.
        """
        s3 = resource(
            service_name='s3',
            region_name=self.aws_region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        input_data_folder = s3.Bucket(self.bucket_name)
        return input_data_folder

    def get_charging_stations_data_raw(self):
        bucket = self.access_evlution_input_s3()
        obj = bucket.Object('input/Ontario_Electric_Charging_Stations.csv').get()
        cs_data = pd.read_csv(obj['Body'])
        return cs_data

    def get_places_data_raw(self):
        bucket = self.access_evlution_input_s3()
        obj = bucket.Object('input/gis_osm_places_a_free_1.csv').get()
        places = pd.read_csv(obj['Body'], sep='\t')
        places = self.pdf_to_gdf(places)
        return places

    def get_traffic_data_raw(self):
        bucket = self.access_evlution_input_s3()
        obj = bucket.Object('input/gis_osm_traffic_a_free_1.csv').get()
        traffic = pd.read_csv(obj['Body'], sep='\t')
        traffic = self.pdf_to_gdf(traffic)
        return traffic

    def get_poi_data_raw(self):
        bucket = self.access_evlution_input_s3()
        obj = bucket.Object('input/gis_osm_pois_a_free_1.csv').get()
        poi = pd.read_csv(obj['Body'], sep='\t')
        poi = self.pdf_to_gdf(poi)
        return poi
