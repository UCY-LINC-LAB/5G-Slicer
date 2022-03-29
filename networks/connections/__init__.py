from abc import ABC, abstractmethod
from dataclasses import dataclass

from networks.QoS import QoS


@dataclass
class Wireless(ABC):


    @abstractmethod
    def get_radius(self):
        raise NotImplementedError

    @abstractmethod
    def get_qos_from(self, *args, **kwargs) -> QoS:
        raise NotImplementedError

    def set_radius(self, radius: int):
        self.radius = radius
        if type(radius) == str:
            self.radius = self.get_radius_in_km(radius)

    @staticmethod
    def get_radius_in_km(radius):
        if radius.lower().endswith("km"):
            return float(radius[:-2])
        if radius.lower().endswith("m"):
            return float(radius[:-1]) / 1000
        raise ValueError("The radius should be either in km or m")