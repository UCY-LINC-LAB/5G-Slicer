import unittest

from networks.connections.mimo import SISO


class TestBaseSISO(unittest.TestCase):

    def setUp(self):
        self.siso_default = SISO()

    def test_radius(self):
        self.assertEqual(self.siso_default.get_radius(), 0.092)

    def test_bandwidth(self):
        self.assertEqual(self.siso_default.get_bandwidth_from_distance(0), self.siso_default.maximum_bitrate * 0.125)
        self.assertEqual(self.siso_default.get_bandwidth_from_distance(10), 528.9034032974349 * 0.125)
        self.assertEqual(self.siso_default.get_bandwidth_from_distance(90), 55.61590262921605 * 0.125)
        self.assertEqual(self.siso_default.get_bandwidth_from_distance(100), 53.87 * 0.125)
        self.assertEqual(self.siso_default.get_bandwidth_from_distance(1000), 53.87 * 0.125)

    def test_error_rate(self):
        self.assertEqual(self.siso_default.get_error_rate(0), 0.0)
        self.assertEqual(self.siso_default.get_error_rate(50), 0.0)
        self.assertEqual(self.siso_default.get_error_rate(70), 8.363754133711154e-08)
        self.assertEqual(self.siso_default.get_error_rate(92), 0.0016055016320071225)
