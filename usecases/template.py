from abc import ABC, abstractmethod

from SlicerSDK import SlicerSDK


class Template(ABC):
    """
    The Use-case template prototype class
    """

    @abstractmethod
    def generate_experiment(self) -> SlicerSDK:
        """
        This method should create the model in a programmable way and introduce it to the SlicerSDK
        :return: A SlicerSdk object
        """
        pass