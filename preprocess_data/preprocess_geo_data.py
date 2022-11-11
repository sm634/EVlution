from preprocess_utils import GeoFabrikData


# instantiate the geo fabrik data class.
gfd = GeoFabrikData()

# retrieve the data with the appropriate transformations for places, traffic and place of interest
toronto_poi = gfd.get_place_poi_gdf('gis_osm_places_a_free_1.shp', 'gis_osm_pois_a_free_1.shp', place='Toronto')
toronto_traffic = gfd.get_place_traffic_gdf('gis_osm_places_a_free_1.shp', 'gis_osm_traffic_a_free_1.shp')
