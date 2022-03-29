import unittest
import yaml

from networks.QoS import QoS
from networks.connections.mathematical_connections import FlatWirelessNetwork, StepWiseDegradation

yaml.Dumper.ignore_aliases = lambda *args : True

class TestFlatWirelessNetworks(unittest.TestCase):
    def setUp(self):
        self.flat_default = FlatWirelessNetwork()

    def test_defaults(self):
        self.assertEqual(self.flat_default.get_qos_from(0.010).get_delay(), 0)
        self.assertEqual(self.flat_default.get_qos_from(0.010).get_bandwidth(), 1000000)
        self.assertEqual(self.flat_default.get_qos_from(0.010).get_error_rate(), 0)
        self.assertEqual(self.flat_default.get_qos_from(0.010).get_deviation(), 0)
        self.assertEqual(self.flat_default.get_radius(), 500)

    def test_qos(self):
        qos = self.flat_default.get_qos_from(0.010)
        expected_qos = QoS(dict(latency=dict(delay=0, deviation=0), bandwidth=1000000, error_rate=0))
        self.assertTrue(qos==expected_qos)

class TestStepWiseNetworks(unittest.TestCase):

    def setUp(self):
        self.step_default = StepWiseDegradation(radius=500, bins={
            '0.5km': dict(latency=dict(delay=1, deviation=1),bandwidth=50000, error_rate=0),
            '1km': dict(latency=dict(delay=10, deviation=3), bandwidth=5000, error_rate=1) })

    def test_defaults(self):
        self.assertEqual(self.step_default.get_qos_from(0.01).get_delay(), 1)
        self.assertEqual(self.step_default.get_qos_from(0.01).get_bandwidth(), 50000)
        self.assertEqual(self.step_default.get_qos_from(0.01).get_error_rate(), 0)
        self.assertEqual(self.step_default.get_qos_from(0.01).get_deviation(), 1)
        self.assertEqual(self.step_default.get_radius(), 500)
        self.assertEqual(self.step_default.get_qos_from(0.501).get_delay(), 10)
        self.assertEqual(self.step_default.get_qos_from(0.501).get_bandwidth(), 5000)
        self.assertEqual(self.step_default.get_qos_from(0.501).get_error_rate(), 1)
        self.assertEqual(self.step_default.get_qos_from(0.501).get_deviation(), 3)