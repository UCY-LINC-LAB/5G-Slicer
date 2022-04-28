from typing import Dict
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import yaml
from ipyleaflet import Map
import pickle
from utils import to_camel_case
from utils.server import APIService
from utils.ui import MobilityMap
import copy

yaml.Dumper.ignore_aliases = lambda *args: True
from FogifySDK.FogifySDK import ExceptionFogifySDK
from FogifySDK import FogifySDK
import networks
from enum import Enum, unique


class SlicerSDK(FogifySDK):
    """
    The basic client library for interaction between the conceptual graph and Fogify deployment
    """

    slices: Dict[str, networks.Slice]
    locations: Dict
    _server: APIService

    @unique
    class LocationType(Enum):
        CLOUD = 'CLOUD'
        EDGE = 'EDGE'
        UE = 'UE'

    location_maps: Dict = {}

    def __init__(self, url: str, docker_compose: str = None):
        self.slices: Dict[str, networks.Slice] = {}
        self.locations = {}
        self._server = APIService(self)
        FogifySDK.__init__(self, url, docker_compose)

    def add_RU_to_slice(self, slice_name: str, lat: float, lon: float, alt: float = None) -> None:
        """
        Introduces a new radio unit to the network slice
        :param slice_name: Network slice name
        :param lat: latitude of the RU
        :param lon: longitude of the RU
        :param alt: altitude in meters of the RU
        """
        selected_network = None
        for slice in self.networks:
            if slice.get('name') == slice_name:
                selected_network = slice
                break
        RUs = selected_network.get('RUs', [])
        RUs.append(dict(lat=lat, lon=lon, alt=alt))
        selected_network['RUs'] = RUs

    def add_topology_node(self, label: str, service: str, device: str, networks: list = [], replicas: int = 1,
                          location_type: LocationType = None, lat: float = None, lon: float = None,
                          alt: float = None) -> None:
        """
        Introduces a new topology (blueprint) node to the model
        :param label: The label (identifier) of the topology node
        :param service: The service that will run on the node
        :param device: The processing capabilities of the node
        :param networks: The networks and the network slices that the node is connected to
        :param replicas: The replication factor
        :param location_type: Location type of the node (CLOUD, EDGE, UE)
        :param lat: latitude of the Node
        :param lon: longitude of the Node
        :param alt: altitude of the Node
        """
        FogifySDK.add_topology_node(self, label, service, device, networks, replicas)
        if lat is not None and lon is not None:
            self.topology[-1]['location'] = {'lat': lat, 'lon': lon}
        if lat is not None and lon is not None and alt is not None:
            self.topology[-1]['location'] = {'lat': lat, 'lon': lon, 'alt': alt}
        if location_type:
            loc = self.topology[-1].get('location', {})
            loc['location_type'] = location_type.value
            self.topology[-1]['location'] = loc

    def generate_slices(self) -> None:
        """
        Generates the Fogify model from the Slices
        """
        self.__import_slices()
        self.__import_mobile_nodes()
        for network_name, network in self.slices.items():
            backhaul_qos = network.get_backhaul().get_formatted_bidirectional_qos()
            self.add_network(network_name, backhaul_qos, backhaul_qos)
            self.__generate_links(network)

    def __generate_links(self, network):
        for from_label, from_location in network.get_nodes().items():
            for to_label, to_location in network.get_nodes().items():
                qos = network.get_qos_between_nodes(from_label, to_label)
                if not qos: continue
                self.add_link(network.get_name(), from_label, to_label,
                              dict(properties=qos.get_formatted_bidirectional_qos()), bidirectional=False)

    def __import_mobile_nodes(self):
        for node in self.topology:
            node_has_location = 'location' in node
            if not node_has_location: continue
            self.__import_mobile_node_to_networks(node)

    def __import_mobile_node_to_networks(self, node):
        for network_name, network in self.slices.items():
            is_node_connected_to_network = network_name in node['networks']
            is_node_connected_to_network = is_node_connected_to_network or network_name in [i.get('name') for i in
                                                                                            node['networks'] if
                                                                                            "name" in i]
            if not is_node_connected_to_network: continue
            network.add_node(node['label'], **node['location'])
        del node['location']

    def __import_slices(self):
        for network in self.networks:
            slice_class = self.__get_slice_class(network)
            if slice_class:
                self.slices[network['name']] = slice_class(**network)
                self.networks.remove(network)

    def __get_slice_class(self, network):
        is_mobile_network = 'network_type' in network
        if not is_mobile_network: return None
        network_class = getattr(networks, to_camel_case(network['network_type']))
        return network_class

    def move_node_to_location(self, slice: str, label: str, lat: float, lon: float, alt: float=0) -> None:
        """
        This function alters the position of a node and updates its QoS respectively
        :param slice: The slice name
        :param label: The label(identifier) of the moving node
        :param lat: New latitude of the node
        :param lon: New longitude of the node
        :param alt: New altitude of the node
        """
        if slice not in self.slices: raise ExceptionFogifySDK(f"The {slice} is not mobile network.")
        network_obj = self.slices[slice]
        old_value_delay = {}
        for label_node in network_obj.get_nodes():
            if label == label_node: continue
            old_value_delay[f"{label_node}-{label}"] = network_obj.get_qos_between_nodes(label_node, label).get_delay()

        network_obj.set_node_location(label, lat, lon, alt)
        links = []
        for label_node in network_obj.get_nodes():
            if label == label_node: continue
            qos = network_obj.get_qos_between_nodes(label, label_node)
            if qos:
                links.append(dict(from_node=label, to_node=label_node,
                              parameters={'properties': qos.get_formatted_bidirectional_qos()},
                              bidirectional=False))
            if old_value_delay[f"{label_node}-{label}"] != network_obj.get_qos_between_nodes(label_node, label).get_delay():
                qos = network_obj.get_qos_between_nodes(label_node, label)
                if qos:
                    links.append(dict(from_node=label_node, to_node=label,
                                  parameters={'properties': qos.get_formatted_bidirectional_qos()},
                                  bidirectional=False))
        self.update_map(slice)
        return self.update_links(slice, links)

    def move_nodes_to_locations(self, slice: str, list_of_nodes: list):
        """
        Moves a set of nodes to their new positions
        :param slice: The name of the slice
        :param list_of_nodes: List of nodes along with their lat, lon, alt
        """
        if slice not in self.slices: raise ExceptionFogifySDK(f"The {slice} is not mobile network.")
        network_obj = self.slices[slice]
        links = []
        for node in list_of_nodes:
            node_name = node.get('label')
            lat = node.get('lat')
            lon = node.get('lon')
            alt = node.get('alt')
            has_all_properties = lat and lon and node_name
            if not has_all_properties: raise ExceptionFogifySDK(f"The {node} is not formatted properly.")
            network_obj.set_node_location(node_name, lat, lon, alt)
            for label in network_obj.get_nodes():
                qos = network_obj.get_qos_between_nodes(node_name, label)
                if not qos: continue
                links.append(dict(from_node=node_name, to_node=label,
                                  parameters={'properties': qos.get_formatted_bidirectional_qos()},
                                  bidirectional=False))
        self.update_map(slice)
        return self.update_links(slice, links)

    def action(self, action_type: str , **kwargs) -> None:
        """
        Updated version of action method to handle also moving actions
        :return:
        """
        if action_type.upper() == "MOVE":
            slice = kwargs.get('slice')
            instance_type = kwargs.get('instance_type')
            lat = kwargs.get('lat')
            lon = kwargs.get('lon')
            alt = kwargs.get('alt', 0.0)
            if not slice: raise ExceptionFogifySDK("Mobility action needs a specific networks")
            if not instance_type: raise ExceptionFogifySDK("Mobility action needs a specific instance")
            if not lat: raise ExceptionFogifySDK("Mobility action needs a specific latitude")
            if not lon: raise ExceptionFogifySDK("Mobility action needs a specific longitude")
            self.move_node_to_location(slice, instance_type, lat, lon, alt)

        else:
            FogifySDK.action(self, action_type, **kwargs)

    def generate_map(self, slice_name: str) -> Map:
        """
        Generates and displays the interactive map
        :param slice_name: The slice name that it will be depicted on the map
        :return: The interactive Map object
        """
        self.check_slice(slice_name)
        network = self.slices.get(slice_name)
        self.location_maps[slice_name] = MobilityMap.generate_map(network, self)
        return self.location_maps[slice_name]

    def update_map(self, slice_name: str)->None:
        """
        Updates the interactive map with current positions
        :param slice_name: The network slice of the map
        """
        try:
            self.check_location_maps(slice_name)
            self.check_slice(slice_name)
            MobilityMap.update_map(self.location_maps[slice_name], self.slices[slice_name])
        except Exception:
            return

    def check_location_maps(self, slice_name: str) -> None:
        """
        Validates if the slice name is valid and there is a map for it
        """
        if slice_name not in self.location_maps:
            raise ExceptionFogifySDK(f"There is no mobile network map with {slice_name} as name")

    def check_slice(self, slice_name):
        """
        Validates if the slice name exists in the model
        """
        if slice_name not in self.slices:
            raise ExceptionFogifySDK(f"There is no mobile network with {slice_name} as name")

    def deploy(self, timeout: int = 120) -> None:
        """
        Deploys the stored model to the fogify and starts the API service for the 5G mobile services
        """
        self._server.stop()
        FogifySDK.deploy(self, timeout)
        self._server = APIService(self)
        self._server.start()

    def undeploy(self, timeout: int = 120) -> None:
        """
        Destroys the deployment
        """
        FogifySDK.undeploy(self, timeout)
        self._server.stop()
    
    def profile(self, label, network_slice, energy_model = None, max_energy_consumption=None, last=None):
        in_prefix = 'network_rx_'
        out_prefix = 'network_tx_'
        df = self.get_metrics_from(label).sort_values(by="count")
        network_in_max =  df[f"{in_prefix}{network_slice}"].diff().max()
        network_out_max =  df[f"{out_prefix}{network_slice}"].diff().max()
        if last:
            df = df[-last:]
        has_energy_model = energy_model is not None and max_energy_consumption is not None 

        attribute_labels=['cpu', 'memory', 'network-in', 'network-out']
        if has_energy_model:
            attribute_labels.append('emergy')

        plot_markers = [0, 20, 40, 60, 80, 100]

        cpu = df.cpu_util.mean()/100
        memory = df.memory_util.mean()/100
        network_in = df[f"{in_prefix}{network_slice}"].diff().mean()

        network_out = df[f"{out_prefix}{network_slice}"].diff().mean()


        network_out_ptc = network_out/network_out_max if network_out_max>0 else 0.0
        network_in_ptc = network_in/network_in_max if network_in_max>0 else 0.0
        stats = [100*cpu, 100*memory, 100*network_out_ptc, 100*network_in_ptc]
        if has_energy_model:
            energy = 100*eval(energy_model)
            stats = [100*cpu, 100*memory, 100*network_out_ptc, 100*network_in_ptc, energy/max_energy_consumption]
        labels = np.array(attribute_labels)
        matplotlib.rc('xtick', labelsize=16) 
        matplotlib.rc('ytick', labelsize=16) 

        angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
        stats = np.concatenate((stats,[stats[0]]))
        angles = np.concatenate((angles,[angles[0]]))

        fig = plt.figure()
        ax = fig.add_subplot(111, polar=True)
        ax.plot(angles, stats, 'o-', linewidth=2)
        ax.set_title(f'Profiling of {label} node')
        ax.fill(angles, stats, alpha=0.25)
        ax.set_thetagrids(angles[:-1] * 180/np.pi, labels)
        plt.yticks(plot_markers)
        ax.grid(True)
        plt.show()
    
    def store(self, filename='slicerSDK'):
        filename+=".pickle"
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    def load(self, filename='slicerSDK'):
        filename += ".pickle"
        with open(filename, 'rb') as f:
            self = pickle.load(f)