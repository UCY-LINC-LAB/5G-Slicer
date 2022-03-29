import unittest

from networks.QoS import QoS


class TestSlices(unittest.TestCase):

    def setUp(self):
        self.qos = QoS({})
        self.params = {'latency': {'delay': '3.0ms', 'deviation': '1.0ms'}, 'bandwidth': '10.0mbps',
                       'error_rate': '1.0%'}
        self.qos_with_params = QoS(self.params)

    def test_validate_constructor(self):
        with self.assertRaises(QoS.QoSException):
            QoS({'test': 'test'})

    def test_set_params(self):
        self.qos.set_params(self.params)
        self.assertEqual(self.qos.get_params(), self.params)

    def test_get_params(self):
        self.assertEqual(self.qos.get_params(), {})
        self.assertEqual(self.qos_with_params.get_params(), self.params)

    def test_set_delay(self):
        self.qos.set_delay(5)
        self.assertEqual(self.qos.get_delay(), 5)
        self.qos.set_delay("5ms")
        self.assertEqual(self.qos.get_delay(), 5)
        with self.assertRaises(QoS.QoSException):
            self.qos.set_delay("nothing")

    def test_get_delay(self):
        self.assertEqual(self.qos_with_params.get_delay(), 3)
        self.assertEqual(self.qos.get_delay(), 0.0)

    def test_set_deviation(self):
        self.qos.set_deviation(5)
        self.assertEqual(self.qos.get_deviation(), 5)
        self.qos.set_deviation("5ms")
        self.assertEqual(self.qos.get_deviation(), 5)
        with self.assertRaises(QoS.QoSException):
            self.qos.set_deviation("nothing")

    def test_set_bandwidth(self):
        self.qos.set_bandwidth(5)
        self.assertEqual(self.qos.get_bandwidth(), 5)
        self.qos.set_bandwidth("5mbps")
        self.assertEqual(self.qos.get_bandwidth(), 5)
        with self.assertRaises(QoS.QoSException):
            self.qos.set_bandwidth("nothing")

    def test_set_bandwidth(self):
        self.qos.set_error_rate(5)
        self.assertEqual(self.qos.get_error_rate(), 5)
        self.qos.set_error_rate("5%")
        self.assertEqual(self.qos.get_error_rate(), 5)
        with self.assertRaises(QoS.QoSException):
            self.qos.set_error_rate("nothing")

    def test_get_deviation(self):
        self.assertEqual(self.qos_with_params.get_deviation(), 1)
        self.assertEqual(self.qos.get_deviation(), 0.0)

    def test_get_bandwidth(self):
        self.assertEqual(self.qos_with_params.get_bandwidth(), 10)
        self.assertEqual(self.qos.get_bandwidth(), 1000000)

    def test_get_deviation(self):
        self.assertEqual(self.qos_with_params.get_deviation(), 1)
        self.assertEqual(self.qos.get_deviation(), 0.0)

    def test_get_error_rate(self):
        self.assertEqual(self.qos_with_params.get_error_rate(), 1.0)
        self.assertEqual(self.qos.get_error_rate(), 0.0)

    def test_get_formated_params(self):
        self.assertEqual(self.qos_with_params.get_formated_qos(), self.params)
        self.assertEqual(QoS(QoS.minimum_qos_dict).get_formated_qos(),
                         {'latency': {'delay': '1000000.0ms', 'deviation': '1000000.0ms'}, 'bandwidth': '0.0mbps',
                             'error_rate': '100.0%'})

    def test_get_formated_bidirectional_params(self):
        self.assertEqual(QoS(QoS.minimum_qos_dict).get_formatted_bidirectional_qos(),
                         {'latency': {'delay': '500000.0ms', 'deviation': '500000.0ms'}, 'bandwidth': '0.0mbps',
                             'error_rate': '50.0%'})

    def test_equals(self):
        self.assertEqual(self.qos_with_params == QoS(self.params), True)
        self.assertEqual(self.qos_with_params == QoS(QoS.minimum_qos_dict), False)
        self.assertEqual(self.qos_with_params == "type_test", False)

    def test_merge(self):
        self.assertEqual(QoS({}).merge(QoS({})).get_formated_qos(),
                         {'latency': {'delay': '0.0ms', 'deviation': '0.0ms'}, 'bandwidth': '1000000.0mbps',
                          'error_rate': '0.0%'})

        self.assertEqual(QoS(
            {'latency': {'delay': '5.0ms', 'deviation': '2.0ms'}, 'bandwidth': '10.0mbps', 'error_rate': '1.0%'}).merge(
            QoS({'latency': {'delay': '2.0ms', 'deviation': '2.0ms'}, 'bandwidth': '5.0mbps',
                 'error_rate': '3.0%'})).get_formated_qos(),
                         {'latency': {'delay': '7.0ms', 'deviation': '4.0ms'}, 'bandwidth': '5.0mbps',
                          'error_rate': '4.0%'})
