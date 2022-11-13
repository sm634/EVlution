"""
An intermediary script using the preprocess and data query modules from preprocess_data to write to model input
directory.
Uses the preprocess.preprocess_utils module and it's GeoLocData class to get data either:
(i) saved in preprocess_data/Data/... directory, (ii) read directly from EVlution S3 bucket
(iii) downloaded from EVlution S3 bucket.
"""

from preprocess_data.preprocess_utils import GeoLocData

# instantiate the geo location data class.
gfd = GeoLocData()

gfd.get_charging_stations_data(city='Mississauga')
charging_stations = gfd.charging_stations

place_poi = gfd.get_place_poi_gdf(place='Mississauga')
place_traffic = gfd.get_place_traffic_gdf(place='Mississauga')

# write data to inputs for model
charging_cols = ['x', 'y', 'Station_Name', 'City']
charging_stations[charging_cols].reset_index(drop=True
                                             ).drop_duplicates(subset=['Station_Name']
                                                               ).to_csv('EVs/inputs/Mississauga_charging_stations.csv')

place_poi_cols = ['poi_x', 'poi_y', 'poi_name', 'poi_area', 'place_name']
place_poi[place_poi_cols].reset_index(drop=True).drop_duplicates(subset=['poi_name']
                                                                 ).to_csv('EVs/inputs/Mississauga_poi_data.csv')

place_traffic_cols = ['traffic_x', 'traffic_y', 'traffic_area', 'place_name']
place_traffic[place_traffic_cols].reset_index(drop=True
                                              ).drop_duplicates().to_csv('EVs/inputs/Mississauga_traffic_data.csv')
