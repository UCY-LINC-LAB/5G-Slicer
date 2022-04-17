import math

from ns import core, propagation, wifi
from ns.mobility import ConstantPositionMobilityModel

from networks.QoS import QoS
from networks.connections import Wireless
from utils.location import Location


def db_to_watt(db):
    return 10 ** (db / 10.0)


class SISO(Wireless):

    # Default propagation model is NS3 Friis model
    propagation_loss_model = propagation.FriisPropagationLossModel()
    # Default error rate mode is set to be the NS3 wifi Dsss model
    error_loss_model = wifi.DsssErrorRateModel()

    def __init__(self, transmit_power=30,  # dbm
                 carrier_frequency=28,  # gigahrz
                 bandwidth=100,  # megahrz
                 UE_noise_figure=7.8,  # db
                 RU_antennas_gain=8,  # db
                 UE_antennas_gain=3,  # db
                 maximum_bitrate=538.71,  # mbits per second
                 minmum_bitrate=53.87,  # mbits per second
                 queuing_delay=2):  # in milliseconds
        self.maximum_bitrate = float(maximum_bitrate)
        self.minmum_bitrate = float(minmum_bitrate)
        self.bandwidth = float(bandwidth) * 1e6  # bandwidth in hertz
        self.carrier_frequency = float(carrier_frequency) * 1e9
        self.propagation_loss_model.SetFrequency(self.carrier_frequency)
        self.UE_noise_figure = float(UE_noise_figure)
        self.queuing_delay = float(queuing_delay)  # The delay is static
        self.transmit_power = float(transmit_power)
        self.RU_antennas_gain = float(RU_antennas_gain)
        self.UE_antennas_gain = float(UE_antennas_gain)

    def get_radius(self) -> float:
        """
        Computed radius based on the provided parameters.
        Specifically, the radius is equal to the distance that
        the bandwidth is getting less than minimum provided bandwidth.
        :return: Radius in km
        """
        for i in range(0, 10000):
            bandwidth = self.get_ideal_bandwidth(i)
            if self.minmum_bitrate > bandwidth:
                break
        return i / 1000

    def calculate_snr_in_db(self, distance) -> float:
        """
        Computes signal to noise ratio
        :param distance: The distance between the receiver and transmitter
        :return: The SNR ratio
        """
        signal = self.compute_signal(distance)
        Nt = -174 + 10 * math.log10(self.bandwidth)  # Noise
        snr = signal - (Nt + self.UE_noise_figure)  # Subtract noise from signal
        return snr

    def compute_signal(self, distance) -> float:
        """
        Generates the RSSI signal
        :param distance: The distance between the receiver and transmitter
        :return: RSSI signal power
        """
        a, b = self.get_points_from_distance(distance)
        negative_propagation_loss = self.propagation_loss_model.CalcRxPower(self.transmit_power, a, b)  # dbm
        negative_propagation_loss -= 30  # to db
        transmit_power_to_db = self.transmit_power - 30
        RSSI = transmit_power_to_db + self.UE_antennas_gain + self.RU_antennas_gain + negative_propagation_loss
        return RSSI

    def get_snr_from_distance(self, distance) -> float:
        """
        Returns the watt representation of SNR
        :param distance: The distance between the receiver and transmitter
        :return: The SNR in watts
        """
        snr = self.calculate_snr_in_db(distance)
        snr = db_to_watt(snr)
        return snr

    def get_ideal_bandwidth(self, distance) -> float:
        """
        Returns the ideal capacity (data rate) of the channel
        :param distance: The distance between the receiver and transmitter
        :return: The ideal capacity
        """
        snr = self.get_snr_from_distance(distance)
        capacity = self.bandwidth * math.log2(1 + snr)
        capacity = capacity / 1e6
        return capacity

    def get_bandwidth_from_distance(self, distance) -> float:
        """
        Limits the data rate between the generated limits
        :param distance: The distance between the receiver and transmitter
        :return: The data rate in mbytes per second
        """
        capacity = self.get_ideal_bandwidth(distance)
        fin_capacity = self.maximum_bitrate
        if capacity >= self.minmum_bitrate and capacity <= self.maximum_bitrate:
            fin_capacity = capacity
        if capacity < self.minmum_bitrate:
            fin_capacity = self.minmum_bitrate

        return fin_capacity * 0.125  # to generate Mbytes per second

    #
    def get_error_rate(self, distance) -> float:
        """
        Returns the error rate based on error_loss_model
        :param distance: The distance between the receiver and transmitter
        :return: Connection's error rate
        """
        snr = self.get_snr_from_distance(distance)
        EbN0 = (snr * self.bandwidth / 1e6) / 2.0  # 2 bits per symbol
        ber = self.error_loss_model.DqpskFunction(EbN0)
        nbits = 100
        return 100 * (1 - math.pow((1.0 - ber), nbits))

    @staticmethod
    def get_points_from_distance(distance):
        a = ConstantPositionMobilityModel()
        b = ConstantPositionMobilityModel()
        a.SetPosition(core.Vector(0, 0, 0))
        b.SetPosition(core.Vector(distance, 0, 0))
        return a, b

    def get_queuing_delay(self) -> float:
        return self.queuing_delay

    def get_qos_from(self, distance, *args, **kwargs) -> QoS:
        distance_in_meters = distance * 1000
        return QoS(dict(latency=dict(delay=self.queuing_delay, deviation=1),
            bandwidth=self.get_bandwidth_from_distance(distance_in_meters),
            error_rate=self.get_error_rate(distance_in_meters)))


class MIMO(SISO):
    def __init__(self, transmit_power=23,  # dbm
                 carrier_frequency=28,  # gigahrz
                 bandwidth=100,  # megahrz
                 UE_noise_figure=0,  # db
                 RU_antennas_gain=8,  # db
                 UE_antennas_gain=3,  # db
                 maximum_bitrate=538.71, minmum_bitrate=53.87, queuing_delay=2, RU_antennas=8, UE_antennas=4):
        SISO.__init__(self, transmit_power,  # dbm
                      carrier_frequency,  # gigahrz
                      bandwidth,  # megahrz
                      UE_noise_figure,  # db
                      RU_antennas_gain,  # db
                      UE_antennas_gain,  # db
                      maximum_bitrate, minmum_bitrate, queuing_delay)
        self.RU_antennas = int(RU_antennas)
        self.UE_antennas = int(UE_antennas)

    def get_qos_from(self, distance, RUs, location: Location, *args, **kwargs) -> QoS:
        """
        Since in a MIMO channel the number of available antennas of an RU is crucial, we update also the RUs' sorting
        """
        def compute_bandwidth(obj, location, RU):  # computes the bandwidth for each RU
            qos = SISO.get_qos_from(obj, location.distance(RU[1]))
            connected_UEs = RU[2]
            available_antennas = obj.RU_antennas - connected_UEs * obj.UE_antennas
            return min([available_antennas, obj.UE_antennas]) * qos.get_bandwidth()

        for RU in RUs:
            RU.append(compute_bandwidth(self, location, RU))
        RUs_ = sorted(RUs, key=lambda RU: RU[2], reverse=True)  # sort RUs by bandwidth
        RU = RUs_[0]  # get the RU with the maximum available bandiwdth
        connected_UEs = RU[2]
        available_antennas = self.RU_antennas - (connected_UEs - 2) * self.UE_antennas
        if available_antennas == 0:  # if there is no available antennas
            return QoS.get_minimum_qos()  # The UE is disconnected
        qos = SISO.get_qos_from(self, location.distance(RU[1]))  # get QoS for single-input-single-output channel
        # compute multi-input-multi-output channel based on
        # mimimun antennas between the available RU antennas and UE antennas
        qos.set_bandwidth(min([available_antennas, self.UE_antennas]) * qos.get_bandwidth())
        return qos
