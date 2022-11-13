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
        obj = bucket.Object('input/gis_osm_places_a_free_1.shp').get()
        places = gpd.read_file(obj['Body'])
        return places

    def get_traffic_data_raw(self):
        bucket = self.access_evlution_input_s3()
        obj = bucket.Object('input/gis_osm_traffic_free_1.shp').get()
        traffic = gpd.read_file(obj['Body'])
        return traffic

    def get_poi_data_raw(self):
        bucket = self.access_evlution_input_s3()
        obj = bucket.Object('input/gis_osm_pois_a_free_1.shp').get()
        places = gpd.read_file(obj['Body'])
        return places
