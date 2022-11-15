"""
An intermediary script using the preprocess and data query modules from preprocess_data to write to model input
directory.
Uses the preprocess.preprocess_utils module and it's GeoLocData class to get data either:
(i) saved in preprocess_data/Data/... directory, (ii) read directly from EVlution S3 bucket
(iii) downloaded from EVlution S3 bucket.
"""

from preprocess_data.preprocess_utils import GeoLocData


# instantiate the geo location data class.
def generate_model_inputs(write_csv=False):
    gfd = GeoLocData()

    area = 'Mississauga'
    gfd.get_charging_stations_data(city=area)
    charging_stations = gfd.charging_stations

    place_poi = gfd.get_place_poi_gdf(place=area)
    place_traffic = gfd.get_place_traffic_gdf(place=area)

    # filter out the output dataframes to only keep relevant columns.
    charging_cols = ['x', 'y', 'Station_Name', 'City']
    place_poi_cols = ['poi_x', 'poi_y', 'poi_name', 'poi_area', 'place_name']
    place_traffic_cols = ['traffic_x', 'traffic_y', 'traffic_area', 'place_name']
    charging_stations = charging_stations[charging_cols]
    place_poi = place_poi[place_poi_cols]
    place_traffic = place_traffic[place_traffic_cols]

    # write data to inputs for model
    if write_csv:
        charging_stations.reset_index(drop=True).drop_duplicates(subset=['Station_Name']).to_csv(
            'EVs/inputs/'+area+'_charging_stations.csv')

        place_poi.reset_index(drop=True).drop_duplicates(subset=['poi_name']
                                                         ).to_csv(
            'EVs/inputs/'+area+'_poi_data.csv')

        place_traffic.reset_index(drop=True
                                  ).drop_duplicates().to_csv(
            'EVs/inputs/'+area+'_traffic_data.csv')

    return charging_stations, place_poi, place_traffic


generate_model_inputs(write_csv=True)
