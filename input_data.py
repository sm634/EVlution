"""
An intermediary script using the preprocess and data query modules from preprocess_data to write to model input
directory.
Uses the preprocess.preprocess_utils module and it's GeoLocData class to get data either:
(i) saved in preprocess_data/Data/... directory, (ii) read directly from EVlution S3 bucket
(iii) downloaded from EVlution S3 bucket.
"""

from preprocess_data.geo_location_formatter import GeoLocData


# instantiate the geo location data class.
def generate_model_inputs(write_csv=False, filter_poi=True, s3=False):
    gfd = GeoLocData(s3=s3)

    area = None
    gfd.get_charging_stations_data(city=area)
    charging_stations = gfd.charging_stations

    place_poi = gfd.get_place_poi_gdf(place=area)
    place_traffic = gfd.get_place_traffic_gdf(place=area)

    # filter out the output dataframes to only keep relevant columns.
    charging_cols = ['x', 'y', 'x_km', 'y_km', 'Station_Name', 'City']
    place_poi_cols = ['poi_x', 'poi_y', 'poi_x_km', 'poi_y_km', 'poi_name', 'poi_area', 'place_name']
    place_traffic_cols = ['traffic_x', 'traffic_y', 'traffic_x_km', 'traffic_y_km', 'traffic_area', 'place_name']
    charging_stations = charging_stations[charging_cols]
    place_poi = place_poi[place_poi_cols]
    place_traffic = place_traffic[place_traffic_cols]

    # putting in specific lat and lng coordinate reference points
    if filter_poi:
        x_min_1 = -81.58
        x_max_1 = -79.01
        x_min_2 = -76.94
        x_max_2 = -74.09
        y_min_1 = 45.674
        y_max_1 = 46.63
        y_min_2 = 44.87
        y_max_2 = 45.41

        place_poi_1 = place_poi[
            (place_poi.poi_x >= x_min_1) &
            (place_poi.poi_x <= x_max_1) &
            (place_poi.poi_y >= y_min_1) &
            (place_poi.poi_y <= y_max_1)
            ]

        place_poi_2 = place_poi[
            (place_poi.poi_x >= x_min_2) &
            (place_poi.poi_x <= x_max_2) &
            (place_poi.poi_y >= y_min_2) &
            (place_poi.poi_y <= y_max_2)
            ]

        # charging stations have be within the min and max boundaries of the poi.
        cs_x_min_1 = place_poi_1.poi_x.min()
        cs_x_max_1 = place_poi_1.poi_x.max()
        cs_y_min_1 = place_poi_1.poi_y.min()
        cs_y_max_1 = place_poi_1.poi_y.max()

        # positions of charging station bounding box 2.
        cs_x_min_2 = place_poi_2.poi_x.min()
        cs_x_max_2 = place_poi_2.poi_x.max()
        cs_y_min_2 = place_poi_2.poi_y.min()
        cs_y_max_2 = place_poi_2.poi_y.max()

        charging_stations_1 = charging_stations[
            (charging_stations.x > cs_x_min_1) &
            (charging_stations.x < cs_x_max_1) &
            (charging_stations.y > cs_y_min_1) &
            (charging_stations.y < cs_y_max_1)
            ]
        charging_stations_2 = charging_stations[
            (charging_stations.x > cs_x_min_2) &
            (charging_stations.x < cs_x_max_2) &
            (charging_stations.y > cs_y_min_2) &
            (charging_stations.y < cs_y_max_2)
            ]

        place_traffic_1 = place_traffic[
            (place_traffic.traffic_x >= x_min_1) &
            (place_traffic.traffic_x <= x_max_1) &
            (place_traffic.traffic_y >= y_min_1) &
            (place_traffic.traffic_y <= y_max_1)
            ]
        place_traffic_2 = place_traffic[
            (place_traffic.traffic_x >= x_min_2) &
            (place_traffic.traffic_x <= x_max_2) &
            (place_traffic.traffic_y >= y_min_2) &
            (place_traffic.traffic_y <= y_max_2)
            ]

        if write_csv:
            charging_stations_1.reset_index(drop=True).drop_duplicates(subset=['Station_Name']).to_csv(
                'EVs/inputs/bounding_box_1_charging_stations.csv')
            charging_stations_2.reset_index(drop=True).drop_duplicates(subset=['Station_Name']).to_csv(
                'EVs/inputs/bounding_box_2_charging_stations.csv')
            place_poi_1.reset_index(drop=True).drop_duplicates(subset=['poi_name']
                                                               ).to_csv(
                'EVs/inputs/bounding_box_1_poi_data.csv')
            place_poi_2.reset_index(drop=True).drop_duplicates(subset=['poi_name']
                                                               ).to_csv(
                'EVs/inputs/bounding_box_2_poi_data.csv')
            place_traffic_1.reset_index(drop=True
                                        ).drop_duplicates().to_csv(
                'EVs/inputs/bounding_box_1_traffic_data.csv')
            place_traffic_2.reset_index(drop=True
                                        ).drop_duplicates().to_csv(
                'EVs/inputs/bounding_box_2_traffic_data.csv')

        print("Data Extraction and Process Done")
    else:

        # write data to inputs for model
        if write_csv:
            charging_stations.reset_index(drop=True).drop_duplicates(subset=['Station_Name']).to_csv(
                'EVs/inputs/' + area + '_charging_stations.csv')

            place_poi.reset_index(drop=True).drop_duplicates(subset=['poi_name']
                                                             ).to_csv(
                'EVs/inputs/' + area + '_poi_data.csv')

            place_traffic.reset_index(drop=True
                                      ).drop_duplicates().to_csv(
                'EVs/inputs/' + area + '_traffic_data.csv')

    print("Data extraction and Process Done.")
    return charging_stations, place_poi, place_traffic


generate_model_inputs(write_csv=True, filter_poi=True, s3=True)
