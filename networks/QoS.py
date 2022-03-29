import copy


class QoS:
    class QoSException(Exception): pass

    # minimum (worst) parameters for a QoS object
    minimum_qos_dict = dict(latency=dict(delay=1000000, deviation=1000000), bandwidth=0, error_rate=100)

    # maximum (best) parameters for a QoS object
    maximum_qos_dict = dict(latency=dict(delay=0.1, deviation=0.1), bandwidth=10000000, error_rate=0.1)

    @classmethod
    def get_minimum_qos(cls) -> 'QoS':
        return QoS(cls.minimum_qos_dict)

    @classmethod
    def get_maximum_qos(cls) -> 'QoS':
        return QoS(cls.maximum_qos_dict)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.get_formated_qos())

    def __init__(self, params: dict = None):
        self.params = params if params else {}
        self.__validate_dict()

    def get_formatted_bidirectional_qos(self) -> dict:
        """
        Returns the QoS as formatted bidirectional QoS (latency and error divided by half)
        :return: A dict representation of QoS
        """
        delay = self.get_delay() / 2 if self.get_delay() else None
        deviation = self.get_deviation() / 2 if self.get_deviation() else None
        error_rate = self.get_error_rate() / 2 if self.get_error_rate() else None
        bandwidth = self.get_bandwidth()
        return self.__format_qos(delay, deviation, bandwidth, error_rate)

    def get_formated_qos(self) -> dict:
        return self.__format_qos(self.get_delay(), self.get_deviation(), self.get_bandwidth(), self.get_error_rate())

    @staticmethod
    def __format_qos(delay, deviation, bandwidth, error_rate) -> dict:
        """
        Formats the QoS as a dict
        :param delay: Delay in milliseconds
        :param deviation: Delay deviation in milliseconds
        :param bandwidth: Data rate
        :param error_rate: Percent error rate
        :return: Formated dict with the parameters
        """
        res = {}
        if delay is not None:
            res['latency'] = {'delay': f'{delay}ms'}
            if deviation is not None:
                res['latency']['deviation'] = f'{deviation}ms'
        if bandwidth is not None: res['bandwidth'] = f'{bandwidth}mbps'
        if error_rate is not None: res['error_rate'] = f'{error_rate}%'
        return res

    def set_delay(self, delay: str):
        obj = self.params.get('latency', {})
        obj['delay'] = delay
        self.params['latency'] = obj
        self.__validate_dict()

    def get_delay(self) -> float:
        delay = self.params.get('latency', {}).get('delay')
        delay_is_set = delay is not None

        if not delay_is_set: return 0.0
        return self.__transform_delays(delay)

    def set_deviation(self, deviation):
        obj = self.params.get('latency', {})
        obj['deviation'] = deviation
        self.params['latency'] = obj
        self.__validate_dict()

    def get_deviation(self):
        deviation = self.params.get('latency', {}).get('deviation')
        deviation_is_set = deviation is not None

        if not deviation_is_set: return 0.0
        return self.__transform_delays(deviation)

    def set_bandwidth(self, bandwidth):
        self.params['bandwidth'] = bandwidth
        self.__validate_dict()

    def get_bandwidth(self):
        bandwidth = self.params.get('bandwidth')
        bandwidth_is_set = bandwidth is not None
        if not bandwidth_is_set: return 1000000
        return self.__transform_bandwidth(bandwidth)

    def set_error_rate(self, error_rate):
        self.params['error_rate'] = error_rate
        self.__validate_dict()

    def get_error_rate(self):
        error_rate = self.params.get('error_rate')
        error_rate_is_set = error_rate is not None
        if not error_rate_is_set: return 0.0
        return self.__transform_error_rate(error_rate)

    def __validate_dict(self):
        """
        Validates if the set parameters are in right format
        """
        temp_params = self.get_params()
        self.set_params({})
        for key in temp_params.keys():
            self.__check_key_validity(key)
        delay = temp_params.get("latency", {}).get("delay")
        deviation = temp_params.get("latency", {}).get("deviation")
        bandwidth = temp_params.get("bandwidth")
        error_rate = temp_params.get("error_rate")
        if delay is not None: self.__transform_delays(delay)
        if deviation is not None: self.__transform_delays(deviation)
        if bandwidth is not None: self.__transform_bandwidth(bandwidth)
        if error_rate is not None: self.__transform_error_rate(error_rate)
        self.set_params(temp_params)

    def __check_key_validity(self, key):
        if key not in ['latency', 'bandwidth', 'error_rate']:
            raise QoS.QoSException(f"{key} is not valid for qos")

    @staticmethod
    def __transform_bandwidth(bandwidth):
        try:
            bandwidth = str(bandwidth).lower().replace("mbps", "")
            return round(float(bandwidth), 3)
        except Exception:
            raise QoS.QoSException("bandwidth does not have the right format")

    @staticmethod
    def __transform_error_rate(error_rate):
        try:
            error_rate = str(error_rate).replace("%", "")
            error_rate = float(error_rate)
            if error_rate > 100:
                error_rate = 100
        except Exception:
            raise QoS.QoSException("Error rate does not have the right format")
        return error_rate

    @staticmethod
    def __transform_delays(delay) -> float:
        try:
            delay = str(delay).replace("ms", "")
            return round(float(delay), 2)
        except Exception:
            raise QoS.QoSException("Delay does not have the right format")

    def get_params(self):
        return self.params

    def set_params(self, params):
        self.params = copy.deepcopy(params)

    def __eq__(self, other):
        if type(other) != QoS: return False
        return self.get_params() == other.get_params()

    def merge(self, qos: 'QoS'):
        """
        This method "adds" two QoS objects.
        Every delay, deviation, and error rate are added while we keep the minimum bandwidth.
        :param qos: The incoming QoS
        :return: The generated sum of QoS objects
        """
        res_qos = QoS()
        self_metric = self.get_delay()
        qos_metric = qos.get_delay()
        res_qos.set_delay(self_metric + qos_metric)

        self_metric = self.get_deviation()
        qos_metric = qos.get_deviation()
        res_qos.set_deviation(self_metric + qos_metric)

        self_metric = self.get_bandwidth()
        qos_metric = qos.get_bandwidth()
        res_qos.set_bandwidth(min(self_metric, qos_metric))

        self_metric = self.get_error_rate()
        qos_metric = qos.get_error_rate()
        res_qos.set_error_rate(self_metric + qos_metric)

        return res_qos

    def __add__(self, other):
        return self.merge(other)
