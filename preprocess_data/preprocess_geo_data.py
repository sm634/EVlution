from preprocess_utils import GeoLocData

# instantiate the geo location data class.
gfd = GeoLocData()

gfd.get_charging_stations_data(city='Mississauga')
charging_stations = gfd.charging_stations

place_poi = gfd.get_place_poi_gdf(place='Mississauga')
place_traffic = gfd.get_place_traffic_gdf(place='Mississauga')
