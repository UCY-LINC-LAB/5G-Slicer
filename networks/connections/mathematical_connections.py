from networks.QoS import QoS
from networks.connections import Wireless
from networks.connections.degradation_functions import LinearDegradationFunction, Log2DegradationFunction, \
    Log10DegradationFunction
from utils.general import Bins


class FunctionalDegradation(Wireless):
    """
    Materializes a generic Class for manipulation of mathematical functions
    """
    class FunctionDegradationNetworkException(Exception): pass

    degradation_function = None

    def __init__(self, **parameters):
        self.__validate_parameters(parameters)
        self.set_radio_access_best_qos(parameters.get('best_qos'))
        self.set_radio_access_worst_qos(parameters.get('worst_qos'))
        self.set_radius(parameters.get('radius'))

    def set_radio_access_best_qos(self, best_qos):
        self.radio_access_best_qos = QoS(best_qos)

    def set_radio_access_worst_qos(self, worst_qos):
        self.radio_access_worst_qos = QoS(worst_qos)

    def get_radio_access_best_qos(self):
        return self.radio_access_best_qos

    def get_radio_access_worst_qos(self):
        return self.radio_access_worst_qos

    def get_degradation_function(self):
        return self.degradation_function

    def get_qos_from(self, distance, *args, **kwargs) -> QoS:
        """
        Returns QoS for specific distance by applying the degradation function
        :param distance: The respective distance
        :return: The generated QoS
        """
        if distance > self.get_radius():
            return QoS.get_minimum_qos()
        qos = QoS()
        df = self.degradation_function
        if df is None:
            raise FunctionalDegradation.FunctionDegradationNetworkException("There is no degradation function.")
        best_qos = self.get_radio_access_best_qos()
        worst_qos = self.get_radio_access_worst_qos()

        delay_function = df(best_qos.get_delay(), worst_qos.get_delay(), self.get_radius(), lower_is_better=True)
        deviation_function = df(best_qos.get_deviation(), worst_qos.get_deviation(), self.get_radius(),
                                lower_is_better=True)
        bandwidth_function = df(worst_qos.get_bandwidth(), best_qos.get_bandwidth(), self.get_radius(),
                                lower_is_better=False)
        error_rate_function = df(best_qos.get_error_rate(), worst_qos.get_error_rate(), self.get_radius(),
                                 lower_is_better=True)

        qos.set_delay(delay_function.apply(distance))
        qos.set_deviation(deviation_function.apply(distance))
        qos.set_bandwidth(bandwidth_function.apply(distance))
        qos.set_error_rate(error_rate_function.apply(distance))
        return qos

    @staticmethod
    def __validate_parameters(parameters):
        _ = FunctionalDegradation
        if not parameters.get('best_qos'):
            raise _.FunctionDegradationNetworkException(f"There is no best_qos function in params {parameters}")
        if not parameters.get('worst_qos'):
            raise _.FunctionDegradationNetworkException(f"There is no worst_qos function in params {parameters}")
        if not parameters.get('radius'):
            raise _.FunctionDegradationNetworkException(f"There is no radius function in params {parameters}")

    def set_radius(self, radius):
        self.radius = radius
        if type(radius) == str:
            self.radius = self.get_radius_in_km(radius)

    def get_radius(self):
        return self.radius


class LinearDegradation(FunctionalDegradation):
    """
    The QoS (from best to worst) follow a linear degradation rate
    """
    degradation_function = LinearDegradationFunction


class Log2Degradation(FunctionalDegradation):
    """
    The QoS (from best to worst) follow a log2 degradation rate
    """
    degradation_function = Log2DegradationFunction


class Log10Degradation(FunctionalDegradation):
    """
    The QoS (from best to worst) follow a log10 degradation rate
    """
    degradation_function = Log10DegradationFunction


class MultiRangeNetwork(Wireless):
    """
    Stepwise QoS for a network. Specifically, the user can define multiple ranges (bins) with multiple QoS parameters
    """

    class MultiRangeNetworkNetworkException(Exception): pass

    def __init__(self, radius: int = 500, bins: dict = {}):
        if len(bins.keys()) < 1:
            raise MultiRangeNetwork.MultiRangeNetworkNetworkException("The network needs at least one bin")
        keys = [self.get_radius_in_km(key) * 1000 for key in bins.keys()]
        keys.sort()
        new_keys = []
        for key in range(int(keys[-1])):
            new_keys.append(key)
        self.bins = Bins(new_keys)
        for i in new_keys:
            for key, qos in bins.items():
                if i <= self.get_radius_in_km(key) * 1000:
                    self.bins[i] = QoS(qos)
                    break
        self.set_radius(radius)

    def get_qos_from(self, distance, *args, **kwargs) -> QoS:
        res =  self.bins[distance * 1000]
        return res

    def get_radius(self):
        return self.radius


class FlatWirelessNetwork(MultiRangeNetwork):
    """
    This class keeps flat QoS in a specific radio unit based on specific radius (km)
    """

    def __init__(self, radius: int = 500,
                 qos={'latency': {'delay': 0, 'deviation': 0}, 'bandwidth': 1000000, 'error_rate': 0}):
        bin_ = self.get_radius_in_km(radius) if type(radius) == str else radius / 1000
        MultiRangeNetwork.__init__(self, radius, bins={f"{bin_}km": qos})
