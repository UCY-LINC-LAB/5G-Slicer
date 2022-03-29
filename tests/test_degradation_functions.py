import unittest

from networks.connections.degradation_functions import LinearDegradationFunction, DegradationFunction, Log2DegradationFunction, \
    Log10DegradationFunction


class TestBaseLinearDegradationFunction(unittest.TestCase):

    def test_higher_is_better(self):
        self.assertEqual(LinearDegradationFunction(10, 100, 10, True).apply(5), 55)
        self.assertEqual(LinearDegradationFunction(10, 100, 10, True).apply(2), 28)

        self.assertEqual(LinearDegradationFunction(10, 100, 10, False).apply(2), 82)
        self.assertEqual(LinearDegradationFunction(10, 100, 10, False).apply(5), 55)

    def test_over_limit_values(self):
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            LinearDegradationFunction(10, 100, 10, True).apply(-15)
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            LinearDegradationFunction(10, 100, 10, False).apply(-15)

        self.assertEqual(LinearDegradationFunction(10, 100, 10, True).apply(15), None)
        self.assertEqual(LinearDegradationFunction(10, 100, 10, False).apply(15), None)

        self.assertEqual(LinearDegradationFunction(10, 100, 10, True).apply(0), 10)
        self.assertEqual(LinearDegradationFunction(10, 100, 10, False).apply(0), 100)

        self.assertEqual(LinearDegradationFunction(10, 100, 10, True).apply(10), 100)
        self.assertEqual(LinearDegradationFunction(10, 100, 10, False).apply(10), 10)

    def test_constructor(self):
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            LinearDegradationFunction(10, 100, 10, None)
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            LinearDegradationFunction(None, 100, 10, True)
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            LinearDegradationFunction(10, None, 10, True)
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            LinearDegradationFunction(10, 100, None, True)


class TestBaseLog2DegradationFunction(unittest.TestCase):

    def test_higher_is_better(self):
        self.assertAlmostEqual(Log2DegradationFunction(10, 100, 0.010, True).apply(0.005), 72.90730039024169)
        self.assertAlmostEqual(Log2DegradationFunction(10, 100, 0.010, True).apply(0.002), 37.09269960975831)

        self.assertAlmostEqual(Log2DegradationFunction(10, 100, 0.010, False).apply(0.002), 72.90730039024169)
        self.assertAlmostEqual(Log2DegradationFunction(10, 100, 0.010, False).apply(0.005), 37.09269960975831)

    def test_over_limit_values(self):
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            Log2DegradationFunction(10, 100, 10, True).apply(-15)
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            Log2DegradationFunction(10, 100, 10, False).apply(-15)

        self.assertEqual(Log2DegradationFunction(10, 100, 10, True).apply(15), None)
        self.assertEqual(Log2DegradationFunction(10, 100, 10, False).apply(15), None)

        self.assertEqual(Log2DegradationFunction(10, 100, 10, True).apply(0), 10)
        self.assertEqual(Log2DegradationFunction(10, 100, 10, False).apply(0), 100)

        self.assertEqual(Log2DegradationFunction(10, 100, 10, True).apply(10), 100)
        self.assertEqual(Log2DegradationFunction(10, 100, 10, False).apply(10), 10)

    def test_constructor(self):
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            Log2DegradationFunction(10, 100, 10, None)
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            Log2DegradationFunction(None, 100, 10, True)
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            Log2DegradationFunction(10, None, 10, True)
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            Log2DegradationFunction(10, 100, None, True)


class TestBaseLog10DegradationFunction(unittest.TestCase):

    def test_higher_is_better(self):
        self.assertAlmostEqual(Log10DegradationFunction(10, 100, 0.010, True).apply(0.005), 72.90730039024169)
        self.assertAlmostEqual(Log10DegradationFunction(10, 100, 0.010, True).apply(0.002), 37.09269960975831)

        self.assertAlmostEqual(Log10DegradationFunction(10, 100, 0.010, False).apply(0.002), 72.90730039024169)
        self.assertAlmostEqual(Log10DegradationFunction(10, 100, 0.010, False).apply(0.005), 37.09269960975831)

    def test_over_limit_values(self):
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            Log10DegradationFunction(10, 100, 10, True).apply(-15)
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            Log10DegradationFunction(10, 100, 10, False).apply(-15)

        self.assertEqual(Log10DegradationFunction(10, 100, 10, True).apply(15), None)
        self.assertEqual(Log10DegradationFunction(10, 100, 10, False).apply(15), None)

        self.assertEqual(Log10DegradationFunction(10, 100, 10, True).apply(0), 10)
        self.assertEqual(Log10DegradationFunction(10, 100, 10, False).apply(0), 100)

        self.assertEqual(Log10DegradationFunction(10, 100, 10, True).apply(10), 100)
        self.assertEqual(Log10DegradationFunction(10, 100, 10, False).apply(10), 10)

    def test_constructor(self):
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            Log10DegradationFunction(10, 100, 10, None)
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            Log10DegradationFunction(None, 100, 10, True)
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            Log10DegradationFunction(10, None, 10, True)
        with self.assertRaises(DegradationFunction.DegradationFunctionException):
            Log10DegradationFunction(10, 100, None, True)
