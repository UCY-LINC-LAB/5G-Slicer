import math
from abc import ABC, abstractmethod


class DegradationFunction(ABC):
    """
    Basic Degradation function implementation. The main functionality is represented by "apply" function.
    The apply takes as input the distance and generates the value of the specific metric
    based on maximum-minimum value and the radius
    """

    def __init__(self, minimum, maximum, radius, lower_is_better):
        if None in [minimum, maximum, radius, lower_is_better]:
            raise DegradationFunction.DegradationFunctionException("Degradation function does not allow None input")
        self.minimum = minimum
        self.maximum = maximum
        self.radius = radius
        self.lower_is_better = lower_is_better

    class DegradationFunctionException(Exception): pass

    @abstractmethod
    def apply(self, value):
        raise NotImplementedError


class LinearDegradationFunction(DegradationFunction):

    def __compute_gradient(self) -> float:
        """
        Computes the linear gradient based on maximum, minimum and radius values
        :return: The respective gradient
        """
        difference = self.maximum - self.minimum
        gradient = abs(difference) / self.radius
        return gradient

    def apply(self, distance):
        if distance < 0.0:
            raise DegradationFunction.DegradationFunctionException("The distance can not be lower than 0")
        if not distance <= self.radius:
            return None
        gradient = self.__compute_gradient()
        if not self.lower_is_better:
            return -1 * gradient * distance + self.maximum
        return gradient * distance + self.minimum


class MathFunction(DegradationFunction):
    """
    General mathematical degradation based on functions like log2 or log10
    """
    math_function = None

    def apply(self, distance):
        if distance < 0.0:
            raise DegradationFunction.DegradationFunctionException("The distance can not be lower than 0")
        if self.math_function is None:
            raise DegradationFunction.DegradationFunctionException("Math function should not be None")
        if not distance <= self.radius:
            return None
        ceil_distance = math.ceil(distance * 1000)
        # The gradient follows the respective mathematical function (math_function)
        a = abs(self.maximum - self.minimum) / self.math_function(self.radius * 1000)
        if not self.lower_is_better:
            res = self.maximum - a * self.math_function(ceil_distance) if ceil_distance >= 1 else self.maximum
        else:
            res = self.minimum + a * self.math_function(ceil_distance) if ceil_distance >= 1 else self.minimum
        return res


class Log2DegradationFunction(MathFunction):
    math_function = math.log2


class Log10DegradationFunction(MathFunction):
    math_function = math.log10
