from typing import List

from ipyleaflet import Circle, AwesomeIcon
from ipyleaflet import Map, basemaps, Marker
from ipywidgets import HTML

from networks import SliceConceptualGraph
from utils.location import Location


class MobilityMap(object):

    @classmethod
    def generate_map(cls, network: SliceConceptualGraph, slicer, **kwargs) -> Map:
        radius = network.get_radius()
        RUs = network.get_RUs()
        nodes = network.get_nodes()
        center = cls.get_center(list(nodes.values()) + list(RUs.values()))
        current_map = Map(basemap=basemaps.OpenStreetMap.Mapnik, center=(center.lat, center.lon), dragging=True,
                          **kwargs)

        for _, loc in RUs.items():
            current_map.add_layer(Circle(location=(loc.lat, loc.lon), radius=int(radius * 1000)))
        for label, loc in nodes.items():
            if loc is None: continue
            is_RU = False
            for _, RU_loc in RUs.items():
                if loc.distance(RU_loc) == 0:
                    is_RU = True
                    break
            label_popup = HTML()
            label_popup.value = label
            if is_RU:
                RU_icon = AwesomeIcon(name='server', marker_color='red', icon_color='black', spin=False)
                current_map.add_layer(
                    Marker(icon=RU_icon, location=(loc.lat, loc.lon), title=label, draggable=False,
                           popup=label_popup))
            else:
                marker = Marker(location=(loc.lat, loc.lon), title=label, draggable=True, popup=label_popup)
                def on_move(new_marker):
                    def func(*args, **kwargs):

                        from datetime import datetime
                        last_time = getattr(on_move, 'last_time')
                        now = datetime.now()

                        if last_time is not None and abs((last_time-now).total_seconds())<5:
                            return
                        on_move.last_time = now

                        location = kwargs.get('location', [])
                        if len(location) == 0:
                            return
                        print(f"move_action {network.get_name()} {new_marker.title} {location}")
                        slicer.move_node_to_location(network.get_name(), new_marker.title, lat=location[0], lon=location[1])
                    return func

                on_move.last_time = None


                marker.on_move(callback=on_move(marker))
                current_map.add_layer(
                    marker)

        return current_map

    @classmethod
    def update_map(cls, map: Map, network: SliceConceptualGraph):
        nodes = network.get_nodes()
        for layer in map.layers:
            layer_title = getattr(layer, 'title', '')
            if layer_title in nodes:
                new_location = (nodes[layer_title].lat, nodes[layer_title].lon)
                has_same_lat = new_location[0] == layer.location[0]
                has_same_lon = new_location[0] == layer.location[1]
                if not has_same_lat or not has_same_lon:
                    layer.location = new_location

    @staticmethod
    def get_center(locations: List[Location]):
        lat, lon, count = 0, 0, 0
        for location in locations:
            if location is None: continue
            lat += location.lat
            lon += location.lon
            count += 1
        return Location(lat / count, lon / count)
