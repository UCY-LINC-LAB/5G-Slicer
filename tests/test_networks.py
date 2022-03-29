import unittest

from networks.QoS import QoS
from networks.connections.mathematical_connections import FunctionalDegradation

from networks.slicing import SliceConceptualGraph
from utils.location import Location


class TestBaseStationLinear(unittest.TestCase):
    def setUp(self):
        self.name = "network"
        self.wireless_connection_type = "LinearDegradation"
        self.backhaul_qos = {'latency': {'delay': '3.0ms', 'deviation': '1.0ms'}, 'bandwidth': '100.0mbps',
                             'error_rate': '1.0%'}
        self.midhaul_qos = {'latency': {'delay': '3.0ms', 'deviation': '1.0ms'}, 'bandwidth': '100.0mbps',
                             'error_rate': '1.0%'}
        self.radio_access_qos = dict(
            best_qos={'latency': {'delay': '5.0ms', 'deviation': '2.0ms'}, 'bandwidth': '10.0mbps',
                      'error_rate': '1.0%'},
            worst_qos={'latency': {'delay': '100.0ms', 'deviation': '20.0ms'}, 'bandwidth': '5.0mbps',
                       'error_rate': '2.0%'}, radius="5km")
        self.network = SliceConceptualGraph(self.name, self.midhaul_qos, self.backhaul_qos, self.radio_access_qos)

    def test_creation(self):
        self.assertEqual(self.network.get_name(), "network")

    def test_get_empty_nodes(self):
        self.assertEqual(self.network.get_nodes(), {})

    def test_add_node(self):
        name, lat, lon = 'node', 33, 40
        lat, lon = 33, 40
        self.network.set_RU(lat, lon)
        self.network.add_node(name, lat, lon)
        self.assertEqual(self.network.get_nodes(), {'node': Location(lat, lon)})
        with self.assertRaises(SliceConceptualGraph.NetworkSliceException):
            self.network.add_node('node', 33, 40)

    def test_get_empty_RUs(self):
        self.assertEqual(self.network.get_RUs(), {})

    def test_set_basetastion(self):
        lat, lon = 33, 40
        self.network.set_RU(lat, lon)
        self.assertEqual(self.network.get_RUs(), {f'{lat}-{lon}': Location(lat, lon)})
        with self.assertRaises(SliceConceptualGraph.NetworkSliceException):
            self.network.set_RU(lat, lon)

    def test_constructor(self):
        with self.assertRaises(FunctionalDegradation.FunctionDegradationNetworkException):
            SliceConceptualGraph('test', {}, {}, {})
            SliceConceptualGraph('test', self.midhaul_qos, {}, {})
            SliceConceptualGraph('test', {}, self.backhaul_qos, {})
            SliceConceptualGraph('test', {}, {}, self.radio_access_qos)

    def test_get_qos(self):
        self.assertEqual(self.network.get_backhaul(), QoS(self.backhaul_qos))

    def test_set_qos(self):
        self.network.set_backhaul(QoS.minimum_qos_dict)
        self.assertEqual(self.network.get_backhaul(), QoS(QoS.minimum_qos_dict))

    def test_qos_from_distance(self):
        self.assertEqual(self.network.get_qos_from(5).get_formated_qos(), self.radio_access_qos.get('worst_qos'))
        self.assertEqual(self.network.get_qos_from(0.0).get_formated_qos(), self.radio_access_qos.get('best_qos'))

    def test_get_node_location(self):
        lat, lon = 33, 40
        self.network.set_RU(lat, lon)
        self.network.add_node('test', 10, 10)
        self.assertEqual(self.network.get_node_location('test2'), None)
        self.assertEqual(self.network.get_node_location('test'), Location(10, 10))

    def test_has_to_pass_through_backhaul(self):
        self.network.set_RU(10, 10)
        self.network.set_RU(20, 20)

        self.network.add_node('source1', 10, 10)
        self.network.add_node('destination1', 10, 10)
        self.network.add_node('destination2', 20, 20)

    def test_set_RUs(self):
        self.network.set_RUs([{'lat': 10, 'lon': 10}, {'lat': 5, 'lon': 5}])
        self.assertEqual(self.network.get_RUs(),
                         {'10-10': Location(**{'lat': 10, 'lon': 10}), '5-5': Location(**{'lat': 5, 'lon': 5})})
        lat, lon = 33, 40
        self.network.set_RU(lat, lon)
        with self.assertRaises(SliceConceptualGraph.NetworkSliceException):
            self.network.set_RUs([{'lat': 10, 'lon': 10}, {'lat': 5, 'lon': 5}])

    def test_set_node_location(self):
        lat, lon = 33, 40
        self.network.set_RU(lat, lon)
        self.network.add_node('destination1', 10, 10)
        self.network.set_node_location('destination1', 20, 20)
        self.assertEqual(self.network.get_node_location('destination1'), Location(20, 20))
        with self.assertRaises(Location.LocationException):
            self.network.set_node_location('destination1', 'test', 20)
        with self.assertRaises(Location.LocationException):
            self.network.set_node_location('destination1', 20, 'test')


class TestBaseLog2Degradation(unittest.TestCase):
    def setUp(self):
        self.name = "network"
        self.wireless_connection_type = "Log2Degradation"
        self.midhaul_qos = {'latency': {'delay': '3.0ms', 'deviation': '1.0ms'}, 'bandwidth': '100.0mbps',
                             'error_rate': '1.0%'}
        self.backhaul_qos = {'latency': {'delay': '3.0ms', 'deviation': '1.0ms'}, 'bandwidth': '100.0mbps',
                             'error_rate': '1.0%'}
        self.radio_access_qos = dict(
            best_qos={'latency': {'delay': '5.0ms', 'deviation': '2.0ms'}, 'bandwidth': '10.0mbps',
                      'error_rate': '1.0%'},
            worst_qos={'latency': {'delay': '100.0ms', 'deviation': '20.0ms'}, 'bandwidth': '5.0mbps',
                       'error_rate': '2.0%'}, radius="5km")
        self.network = SliceConceptualGraph(self.name, self.midhaul_qos, self.backhaul_qos, self.radio_access_qos)

    def test_creation(self):
        self.assertEqual(self.network.get_name(), "network")

    def test_get_empty_nodes(self):
        self.assertEqual(self.network.get_nodes(), {})

    def test_add_node(self):
        name, lat, lon = 'node', 33, 40
        with self.assertRaises(SliceConceptualGraph.NetworkSliceException):
            self.network.add_node(name, lat, lon)
        self.network.set_RU(33, 40, 0)
        self.network.add_node(name, lat, lon)
        self.assertEqual(self.network.get_nodes(), {'node': Location(lat, lon)})
        with self.assertRaises(SliceConceptualGraph.NetworkSliceException):
            self.network.add_node('node', 33, 40)

    def test_get_empty_RUs(self):
        self.assertEqual(self.network.get_RUs(), {})

    def test_set_basetastion(self):
        lat, lon = 33, 40
        self.network.set_RU(lat, lon)
        self.assertEqual(self.network.get_RUs(), {f'{lat}-{lon}': Location(lat, lon)})
        with self.assertRaises(SliceConceptualGraph.NetworkSliceException):
            self.network.set_RU(lat, lon)

    def test_constructor(self):
        with self.assertRaises(FunctionalDegradation.FunctionDegradationNetworkException):
            SliceConceptualGraph('test', {} ,{}, {})
            SliceConceptualGraph('test', self.midhaul_qos, {}, {})
            SliceConceptualGraph('test', {}, self.backhaul_qos, {})
            SliceConceptualGraph('test', {}, {}, self.radio_access_qos)

    def test_get_qos(self):
        self.assertEqual(self.network.get_backhaul(), QoS(self.backhaul_qos))

    def test_set_qos(self):
        self.network.set_backhaul(QoS.minimum_qos_dict)
        self.assertEqual(self.network.get_backhaul(), QoS(QoS.minimum_qos_dict))

    def test_qos_from_distance(self):
        self.assertEqual(self.network.get_qos_from(5).get_formated_qos(), self.radio_access_qos.get('worst_qos'))
        self.assertEqual(self.network.get_qos_from(0.0).get_formated_qos(), self.radio_access_qos.get('best_qos'))

    def test_get_node_location(self):
        lat, lon = 33, 40
        self.network.set_RU(lat, lon)
        self.network.add_node('test', 10, 10)
        self.assertEqual(self.network.get_node_location('test2'), None)
        self.assertEqual(self.network.get_node_location('test'), Location(10, 10))

    def test_set_RUs(self):
        self.network.set_RUs([{'lat': 10, 'lon': 10}, {'lat': 5, 'lon': 5}])
        self.assertEqual(self.network.get_RUs(),
                         {'10-10': Location(**{'lat': 10, 'lon': 10}), '5-5': Location(**{'lat': 5, 'lon': 5})})
        with self.assertRaises(SliceConceptualGraph.NetworkSliceException):
            self.network.set_RUs([{'lat': 10, 'lon': 10}, {'lat': 5, 'lon': 5}])

    def test_set_node_location(self):
        lat, lon = 33, 40
        self.network.set_RU(lat, lon)
        self.network.add_node('destination1', 10, 10)
        self.network.set_node_location('destination1', 20, 20)
        self.assertEqual(self.network.get_node_location('destination1'), Location(20, 20))
        with self.assertRaises(Location.LocationException):
            self.network.set_node_location('destination1', 'test', 20)
        with self.assertRaises(Location.LocationException):
            self.network.set_node_location('destination1', 20, 'test')
