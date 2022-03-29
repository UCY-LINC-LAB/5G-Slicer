from typing import Dict

import networkx as nx

from networks.QoS import QoS
from networks.connections import Wireless, prototype_networks
from networks.connections.mathematical_connections import LinearDegradation
from utils.location import Location


class SliceConceptualGraph:
    """
    This class keeps information about the connections of a network slice such as nodes, connections, their QoS, etc
    Its parameters include:
    - wireless_connection: the degradation model that RU-to-UE connections will follow based on distance
    - graph: the in-memory graph that keeps all information about the topology
    - backhaul: QoS characteristics of the RU-to-Cloud connections
    - midhaul: QoS characteristics of the RU-to-RU connections or/and Edge-to-Edge connections
    """
    wireless_connection: Wireless
    graph: nx.Graph
    backhaul: QoS
    midhaul: QoS

    class NetworkSliceException(Exception): pass

    def __init__(self, name, backhaul_qos, midhaul_qos, radio_access_qos, RUs=[],
                 wireless_connection_type="LinearDegradation", **kwargs):
        self.graph = nx.Graph()
        self.graph.name = name
        self.set_backhaul(backhaul_qos)
        self.set_midhaul(midhaul_qos)
        WirelessClass = getattr(prototype_networks, wireless_connection_type, LinearDegradation)
        self.wireless_connection = WirelessClass(**radio_access_qos)
        self.set_cloud_connection()
        self.set_RUs(RUs)

    def set_cloud_connection(self) -> None:
        """
        Creates a virtual node that inter-connects the Cloud instances with the rest of RUs
        """
        self.graph.add_node('cloud_connection', location=None, type='RU')

    def get_backhaul(self) -> QoS:
        """
        :return: Backhaul QoS of the network Slice
        """
        return self.backhaul

    def get_midhaul(self) -> QoS:
        """
        :return: Midhaul QoS of the network Slice
        """
        return self.midhaul

    def set_RUs(self, RUs) -> None:
        """
        Put RUs to the network
        :param RUs: A set of RUs (especially an RU needs only a <x, y, z> location)
        """
        for RU in RUs:
            self.set_RU(**RU)

    def set_backhaul(self, backhaul_qos: Dict) -> None:
        """
        Set Backhaul QoS to the object
        :param backhaul_qos: Backhaul QoS in dict representation
        """
        self.backhaul = QoS(backhaul_qos)

    def set_midhaul(self, midhaul_qos) -> None:
        """
        Set Midhaul QoS to the object
        :param midhaul_qos: Backhaul QoS in dict representation
        """
        self.midhaul = QoS(midhaul_qos)

    def get_name(self) -> str:
        """
        Returns the slice name
        :return: Slice name
        """
        return self.graph.name

    def get_nodes(self) -> Dict[str, Location]:
        """
        Retrieves all nodes with compute capabilities from a network (UEs, EDGE, CLOUD)
        :return: All compute nodes (UEs, EDGE, CLOUD)
        """
        return {name: data['location'] for name, data in self.graph.nodes(data=True) if
                data.get('type') in ['UE', 'EDGE', 'CLOUD']}

    def add_node(self, name: str, lat: float = None, lon: float = None, alt: float = None,
                 location_type: str = None) -> None:
        """
        Creates and adds a node to the graph. Need to have a name as identifier.
        Furthermore, for UEs and Edge nodes we need at least lat and lon (alt is optional).
        For cloud nodes we need the location_type to be set equals to "CLOUD"
        :param name: Node's identifier
        :param lat: Latitude
        :param lon: Longitude
        :param alt: Altitude
        :param location_type: Location type could be either EDGE (for edge nodes) or CLOUD
        """
        RUs = self.get_RUs()
        if location_type is None:
            location_type = 'UE'
        self.__check_validity_of_node_params(RUs, name, lat, lon, location_type)

        funtions = dict(
            UE=self.add_UE_node,
            EDGE=self.add_edge_node,
            CLOUD=self.add_cloud_node
            )
        add_node_funtion = funtions.get(location_type,
            lambda **kwars: self.NetworkSliceException(f"The location_type is {location_type} but it should be either 'UE' or 'EDGE' or 'CLOUD'"))
        location = Location(lat, lon, alt) if None not in (lat, lon) else None

        add_node_funtion(name=name, location=location)

    def __check_validity_of_node_params(self, RUs, name, lat, lon, location_type):
        # Check validity of the inputs
        if len(RUs) < 1:
            raise self.NetworkSliceException("You have to add first all base stations")
        if name in self.graph:
            raise self.NetworkSliceException("Node already exists")
        if lat is None and lon is None and location_type != 'CLOUD':
            raise self.NetworkSliceException(
                "A Node need either to be CLOUD node or to have at least latitude and longitude")

    def add_cloud_node(self, name: str, **kwargs):
        # We connect any CLOUD node to the cloud_connection (cloud-to-RUs)
        self.graph.add_node(name, location=None, type='CLOUD')
        self.graph.add_edge(name, 'cloud_connection', qos=self.get_backhaul())

    def add_edge_node(self, name: str, location: Location):
        self.graph.add_node(name, location=location, type='EDGE')
        # Edge should be colocated with RU so if RU with same location with Edge exists, we connect Edge to it
        RU, qos = self.get_qos_for_selected_RU(location)
        selected_RU = RU[0]
        if RU[1].distance(location) != 0:  # otherwise we create a new RU at the same location
            selected_RU = self.set_RU(location.lat, location.lon, location.alt)

        # We connect EDGE to respective RU with the best QoS of our system
        self.graph.add_edge(name, selected_RU, qos=QoS.get_maximum_qos())

    def add_UE_node(self, name, location):
        # UE is connected to the closest RU
        self.graph.add_node(name, location=location, type='UE')
        RU, qos = self.get_qos_for_selected_RU(location)
        self.graph.add_edge(name, RU[0], qos=qos)



    def get_qos_for_selected_RU(self, location: Location) -> (str, QoS):
        """
        This method computes the QoS of a specific location
        :param location: Instance of Location class
        :return: A pair of RU-id (str) and the respective QoS
        """
        RUs = self.__get_sorted_RUs(location)
        if len(RUs) == 0:
            return None
        min_distance = RUs[0][1].distance(location)
        if min_distance > self.get_radius():
            return RUs[0], QoS.get_minimum_qos()
        qos = self.wireless_connection.get_qos_from(distance=min_distance, RUs=RUs, location=location)
        return RUs[0], qos

    def get_RUs(self, with_cloud=False) -> Dict[str, Location]:
        """
        Returns RU nodes of the network. Since, we design the cloud-to-RUs connection as RU node,
        we introduce a parameter `with_cloud` which declares that
        if the returned RUs will include or not the cloud connection
        :param with_cloud: Declares if the results will include conceptual RU-cloud connection
        :return: A dictionary of RU-ids and their locations
        """
        if with_cloud:
            return {name: data.get('location') for name, data in self.graph.nodes(data=True) if
                    data.get('type') == 'RU'}
        return {name: data.get('location') for name, data in self.graph.nodes(data=True) if
                data.get('type') == 'RU' and data.get('location') is not None}

    def _get_RU_key(self, lat, lon, alt):
        return f"{lat}-{lon}" if alt is None else f"{lat}-{lon}-{alt}"

    def set_RU(self, lat, lon, alt=None) -> None:
        """
        Introduce a new RU to the network
        :param lat: RU's latitude
        :param lon: RU's longitude
        :param alt: RU's altitude
        """
        if 0 < len(self.get_nodes()):
            raise self.NetworkSliceException("You can not add RU after network creation")
        key = self._get_RU_key(lat, lon, alt)
        if key in self.graph: raise self.NetworkSliceException("The RU exists")
        self.graph.add_node(key, location=Location(lat, lon, alt), type='RU')
        for RU in self.get_RUs(with_cloud=True):
            self.graph.add_edge(key, RU, qos=self.get_midhaul())  # Every RU is connected with each other via midhaul
        return key

    def get_radius(self) -> float:
        """
        :return: Radius from the wireless connection
        """
        return self.wireless_connection.get_radius()

    def get_qos_from(self, distance, *args, **kwargs):
        """
        Returns QoS for a Specific Distance between RUs and UE
        :param distance: RU-to-UE distance
        """
        return self.wireless_connection.get_qos_from(distance, *args, **kwargs)

    def has_to_pass_through_midhaul(self, source_node, destination_node) -> bool:
        """
        Returns if the communication between two nodes passes through RU-to-RU link
        :param source_node: The source node of the path
        :param destination_node: The destination node of the path
        """
        source_neighbors = [i for i in self.graph.neighbors(source_node)]
        destination_neighbors = [i for i in self.graph.neighbors(destination_node)]
        return not source_neighbors[0] == destination_neighbors[0]

    def get_node_location(self, node_name) -> Location:
        """
        Returns the location of a node
        :param node_name: The node name (identifier)
        """
        if node_name in self.graph.nodes:
            return self.graph.nodes[node_name]['location']

    def __get_sorted_RUs(self, location: Location) -> list[Location]:
        """
        Sort RUs by distance from a location
        """
        res = []
        RUs = self.get_RUs()
        for RU, bs_location in self.get_RUs().items():
            if bs_location is None: continue
            res.append([RU, bs_location, len([i for i in self.graph.neighbors(RU) if i not in RUs])])
        return sorted(res, key=lambda x: x[1].distance(location), reverse=False)

    def set_node_location(self, node_name, lat, lon, alt=0.0) -> None:
        """
        Updates the node's location
        :param node_name: Node's identifier
        :param lat: Latitude of the new position
        :param lon: Longitude of the new position
        :param alt: Altitude of the new position
        """
        node_location = self.get_node_location(node_name)
        node_location.set_lat(lat)
        node_location.set_lon(lon)
        node_location.set_alt(alt)
        edges = self.graph.edges([node_name])
        self.graph.remove_edges_from(list(edges))
        self.graph.remove_node(node_name)
        self.add_node(node_name, lat, lon, alt)
        RU, qos = self.get_qos_for_selected_RU(node_location)
        self.graph.add_edge(node_name, RU[0], qos=qos)

    def get_qos_between_nodes(self, from_node, to_node) -> QoS:
        """
        Generates the QoS for the shortest path between two nodes.
        :param from_node: The source node of the path
        :param to_node: The destination node of the path
        :return: The respective QoS
        """
        if from_node == to_node: return
        p = nx.shortest_path(self.graph, source=from_node, target=to_node)
        path_graph = list(nx.path_graph(p).edges())
        qos = QoS()
        ea = path_graph[0]
        edge = self.graph.edges[ea[0], ea[1]]
        qos = qos + edge['qos'] + edge['qos']
        for ea in path_graph[1:-1]:
            edge = self.graph.edges[ea[0], ea[1]]
            qos = qos + edge['qos']
        ea = path_graph[-1]
        edge = self.graph.edges[ea[0], ea[1]]
        qos = qos + edge['qos'] + edge['qos']
        return qos
