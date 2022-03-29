import unittest
from pathlib import Path

import yaml

yaml.Dumper.ignore_aliases = lambda *args: True
from SlicerSDK import SlicerSDK

file_path = f"{Path(__file__).parent.absolute()}/"


class TestSlices(unittest.TestCase):
    def setUp(self):
        self.linear_mobi = SlicerSDK('http://controller:5000', f"{file_path}lineardegradation/docker-compose.yaml")
        self.flat_mobi = SlicerSDK('http://controller:5000', f"{file_path}flat/docker-compose.yaml")
        self.siso_mobi = SlicerSDK('http://controller:5000', f"{file_path}siso-mimo/siso-docker-compose.yaml")
        self.mimo_mobi = SlicerSDK('http://controller:5000', f"{file_path}siso-mimo/mimo-docker-compose.yaml")

    def test_linear_constructed_object(self):
        self.linear_mobi.generate_slices()
        self.linear_mobi.upload_file(False)
        correct = yaml.load(open(f"{file_path}lineardegradation/fogified-docker-compose_correct.yaml", "r"))
        generated = yaml.load(open(f"fogified-docker-compose.yaml", "r"))
        self.assertEqual(correct, generated)

    def test_flat_constructed_object(self):
        self.flat_mobi.generate_slices()
        self.flat_mobi.upload_file(False)
        correct = yaml.load(open(f"{file_path}flat/fogified-docker-compose_correct.yaml", "r"))
        generated = yaml.load(open(f"fogified-docker-compose.yaml", "r"))
        self.assertEqual(correct, generated)

    def test_siso_constructed_object(self):
        self.siso_mobi.generate_slices()
        self.siso_mobi.upload_file(False)
        correct = yaml.load(open(f"{file_path}siso-mimo/siso-correct-docker-compose.yaml", "r"))
        generated = yaml.load(open(f"fogified-docker-compose.yaml", "r"))
        self.assertEqual(correct, generated)

    def test_mimo_constructed_object(self):
        self.mimo_mobi.generate_slices()
        self.mimo_mobi.upload_file(False)
        correct = yaml.load(open(f"{file_path}siso-mimo/mimo-correct-docker-compose.yaml", "r"))
        generated = yaml.load(open(f"fogified-docker-compose.yaml", "r"))
        self.assertEqual(correct, generated)
