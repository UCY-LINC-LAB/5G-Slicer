import copy
import unittest
from pathlib import Path

from SlicerSDK import SlicerSDK
from usecases.dublin_buses_experiment import BusExperiment

file_path = f"{Path(__file__).parent.absolute()}/docker-compose-dublin.yaml"


class TestDublinBusesExperiment(unittest.TestCase):

    def setUp(self):
        self.slicerSDK = SlicerSDK("http://controller:5000", file_path)

    def test_default_init(self):
        experiment = BusExperiment(self.slicerSDK, traces_filename="all.csv", bus_stops_filename="stops.csv")
        self.assertEqual(experiment.bounding_box,
                         ((53.33912464060235, -6.286239624023438), (53.35833815100412, -6.226158142089845)))
        self.assertEqual(experiment.num_of_RUs, 1)
        self.assertEqual(experiment.num_of_edge, 1)
        self.assertEqual(experiment.num_of_buses, 1)
        self.assertEqual(experiment.time_to_run, 60)
        self.assertEqual(experiment.traces_filename, f'all.csv')
        self.assertEqual(experiment.bus_stops_filename, f'stops.csv')
        self.assertEqual(experiment.edge_service, 'edge_service')
        self.assertEqual(experiment.edge_device, 'edge_device')
        self.assertEqual(experiment.bus_device, 'bus_device')
        self.assertEqual(experiment.slice_name, 'dublin_network')
        self.assertEqual(experiment.min_num_of_trace_steps, 0)
        self.assertEqual(experiment.max_num_of_trace_steps, 60)
        self.assertEqual(experiment.ru_overlap, 'random')

    def test_init_with_more_compute_nodes_than_bs(self):
        experiment = BusExperiment(self.slicerSDK, num_of_edge=5, num_of_RUs=2, traces_filename="all.csv",
                                   bus_stops_filename="stops.csv")
        self.assertEqual(experiment.num_of_edge, 2)

    def test_generate_documents(self):
        res = {}
        for bsoverlap in ['max_density', 'min_density', 'random', 'none']:
            self.slicerSDK = SlicerSDK("http://controller:5000", file_path)
            experiment = BusExperiment(self.slicerSDK, traces_filename="all.csv", bus_stops_filename="stops.csv",
                                       num_of_RUs=5, num_of_buses=10, num_of_edge=5, ru_overlap=bsoverlap,
                                       bounding_box=((53.34483836229132, -6.274480819702148),
                                                     (53.34996212515024, -6.244525909423829)))
            experiment.generate_experiment()
            self.assertEqual(len(experiment.RUs), 5)
            self.slicerSDK = SlicerSDK("http://controller:5000", file_path)
            experiment = BusExperiment(self.slicerSDK, traces_filename="all.csv", bus_stops_filename="stops.csv",
                                       num_of_RUs=100, num_of_buses=10, num_of_edge=5)
            experiment.generate_experiment()
            self.assertEqual(len(experiment.RUs), 100)
            res[bsoverlap] = copy.deepcopy(experiment.RUs)
        self.assertNotEquals(res['max_density'], res['min_density'])
