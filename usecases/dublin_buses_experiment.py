import copy
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple, List

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from SlicerSDK import SlicerSDK
from usecases.template import Template
from utils.location import Location


@dataclass
class BusExperiment(Template):
    """
    Smart city usecase that generated from the Dublin's datasets.
    Users have to specify a set of parameters
    """
    slicer_sdk: SlicerSDK
    bounding_box: Tuple[Tuple] = ((53.33912464060235, -6.286239624023438), (53.35833815100412, -6.226158142089845))
    num_of_RUs: int = 1
    num_of_edge: int = 1
    num_of_clouds: int = 1
    num_of_buses: int = 1
    time_to_run: int = 60
    traces_filename: str = 'usecases/data/all.csv'
    bus_stops_filename: str = 'usecases/data/stops.csv'
    edge_service: str = 'edge_service'
    edge_device: str = 'edge_device'
    bus_service: str = 'bus_service'
    bus_device: str = 'bus_device'
    cloud_service: str = 'cloud_service'
    cloud_device: str = 'cloud_machine'
    slice_name: str = 'dublin_network'
    max_num_of_trace_steps: int = 60
    min_num_of_trace_steps: int = 0
    bus_ids: List[int] = None
    bs_overlap: str = "random"  # or max_density, min_density, kmeans

    def __post_init__(self):
        if self.num_of_edge > self.num_of_RUs:
            self.num_of_edge = self.num_of_RUs
        self.fill_trace_dataframe()
        self.fill_stops_dataframe()
        self.fill_traces()
        self.__RUs = []
        self.__compute_nodes = []
        if self.bus_ids is None:
            self.bus_ids = []

    def fill_stops_dataframe(self):
        self.stop_df = pd.read_csv(self.bus_stops_filename)
        self.stop_df = self.return_for_bounds(self.stop_df)

    @property
    def RUs(self):
        records = self.stop_df.to_dict('records')
        if self.__RUs == []:
            if self.bs_overlap in ['min_density', 'max_density']:
                self.__density_based_RUs(records)
            elif self.bs_overlap == 'kmeans':
                self.___cluster_based_RUs(records)
            else:
                self.__random_based_RUs(records)
        return self.__RUs

    def __random_based_RUs(self, records):
        try:
            self.__RUs = random.sample(records, k=self.num_of_RUs)
        except Exception as ex:
            print(ex)
            pass

    def ___cluster_based_RUs(self, records):
        X = np.array([[RU['Lat'], RU['Lon']] for RU in records])
        kmeans = KMeans(n_clusters=self.num_of_RUs, random_state=0).fit(X)
        fin_res = []
        for points in kmeans.cluster_centers_:
            for RU in records:
                if RU['Lat'] == points[0] and RU['Lon'] == points[1]:
                    fin_res.append(RU)
                    break
        self.__RUs = fin_res

    def __density_based_RUs(self, records):
        RU_dists = {}
        for RU_1 in records:
            RU_dists[RU_1['stop_id']] = 0
            for RU_2 in records:
                RU_dists[RU_1['stop_id']] += Location(RU_1['Lat'],
                                                                        RU_1['Lon']).distance(
                    Location(RU_2['Lat'], RU_2['Lon']))
        records.sort(key=lambda x: RU_dists[x['stop_id']])
        if self.bs_overlap == 'min_density':
            self.__RUs = records[:self.num_of_RUs]
        else:
            self.__RUs = records[-self.num_of_RUs:]

    @property
    def compute_nodes(self):
        try:
            self.__compute_nodes = random.sample(self.RUs, k=self.num_of_edge)
        except Exception as ex:
            pass
        return self.__compute_nodes

    def fill_trace_dataframe(self):
        header = ['Timestamp', 'LineID', 'Direction', 'PatternID', 'TimeFrame', 'JourneyID', 'Operator', 'Congestion',
                  'Lon', 'Lat', 'Delay', 'BlockID', 'VehicleID', 'StopID', 'AtStop']
        types = {'Timestamp': np.int64, 'JourneyID': np.int32, 'Congestion': np.int8, 'Lon': np.float64,
                 'Lat': np.float64, 'Delay': np.int8, 'VehicleID': np.int32, 'AtStop': np.int8}
        self.trace_df = pd.read_csv(self.traces_filename, header=None, names=header, dtype=types,
                                    parse_dates=['TimeFrame'], infer_datetime_format=True)
        self.trace_df = self.return_for_bounds(self.trace_df)
        self.trace_df = self.trace_df.sort_values(by=['Timestamp'])
        self.trace_df['trace_id'] = self.trace_df['JourneyID'] + 10000 * self.trace_df["VehicleID"]
        self.trace_df = self.return_for_bounds(self.trace_df)

    def return_for_bounds(self, df):
        bound_a, bound_b = self.bounding_box
        new_df = df
        new_df = new_df[bound_a[0] < new_df['Lat']]
        new_df = new_df[bound_b[0] > new_df['Lat']]
        new_df = new_df[bound_a[1] < new_df['Lon']]
        new_df = new_df[bound_b[1] > new_df['Lon']]
        return new_df

    def fill_traces(self):
        _traces = self.__group_trace_by_id()
        _traces = self.__update_traces_step(_traces)
        self.traces = _traces

    def __update_traces_step(self, _traces):
        traces = {}
        for trace in _traces:
            item = _traces[trace]
            item.sort(key=lambda x: x['timestamp'])
            new_item = []
            for i in range(len(item)):
                start = item[i]
                start['timestamp'] = datetime.fromtimestamp(int(start['timestamp'] / 1000000))

                start_timestamp = start['timestamp']
                is_at_the_same_place = False
                if len(new_item) > 0:
                    is_at_the_same_place = new_item[-1]['Lat'] == start['Lat'] and new_item[-1]['Lon'] == start['Lon']
                if not is_at_the_same_place:
                    new_item.append({'timestamp': start_timestamp, 'Lat': start['Lat'], 'Lon': start['Lon']})
            traces[trace] = new_item
        fin_traces = {}
        if self.bus_ids and len(self.bus_ids) > 0:
            for trace_id in self.bus_ids:
                if trace_id in traces:
                    fin_traces[trace_id] = traces[trace_id]
        else:
            for key, trace in traces.items():
                if len(trace) <= self.max_num_of_trace_steps and len(trace) >= self.min_num_of_trace_steps:
                    fin_traces[key] = trace
                if len(fin_traces) == self.num_of_buses:
                    break
        return fin_traces

    def __group_trace_by_id(self):
        traces = {}
        self.trace_df = self.return_for_bounds(self.trace_df)
        for record in self.trace_df[['Lat', 'Lon', 'trace_id', 'Timestamp']].to_dict('records'):
            traces[record['trace_id']] = traces.get(record['trace_id'], []) + [
                {'Lat': record['Lat'], 'Lon': record['Lon'], 'timestamp': record['Timestamp']}]
        return traces

    def generate_experiment(self)->SlicerSDK:
        self.__generate_experiment_RUs()
        self.__generate_experiment_bus_nodes()
        self.__generate_experiment_edge_nodes()
        self.__generate_experiment_cloud_nodes()
        self.__generate_mobility_scenario()
        self.slicer_sdk.generate_slices()
        return self.slicer_sdk

    def __generate_mobility_scenario(self):
        actions = []
        for trace_id, trace in self.traces.items():
            if trace == []: continue
            initial_timestamp = trace[0]['timestamp']
            for position, location in enumerate(trace):
                time_ = abs(int((location['timestamp'] - initial_timestamp).seconds))
                actions.append({'time': time_, 'instance_type': f"bus_{trace_id}", 'instances': 1,
                                'action': {'type': 'move',
                                           'parameters': {'slice': self.slice_name, 'lat': location['Lat'],
                                                          'lon': location['Lon']}}})
        actions.sort(key=lambda x: x['time'])
        count = 0
        new_actions = []
        for position, action in enumerate(actions[1:]):
            if actions[position]['time'] == 0: continue
            new_action = copy.copy(actions[position])
            new_action['time'] = new_action['time'] - actions[position - 1]['time']
            same_action_same_time = new_action['time'] == 0 and new_action['instance_type'] == actions[position - 1][
                'instance_type']
            if same_action_same_time: continue
            new_action['position'] = count

            new_actions.append(new_action)
            count += 1
        scenario = {'name': 'mobility_scenario', 'actions': new_actions}
        self.slicer_sdk.scenarios.append(scenario)

    def __generate_experiment_cloud_nodes(self):
        for cloud_id in range(self.num_of_clouds):
            self.slicer_sdk.add_topology_node(label=f"CLOUD_{cloud_id}",
                                              service=self.cloud_service,
                                              device=self.cloud_device,
                                              networks=[self.slice_name],
                                              location_type=SlicerSDK.LocationType.CLOUD)

    def __generate_experiment_edge_nodes(self):
        for compute_service in self.compute_nodes:
            self.slicer_sdk.add_topology_node(label=f"EDGE_{compute_service['stop_id']}",
                                              service=self.edge_service, device=self.edge_device,
                                              networks=[self.slice_name], lat=compute_service['Lat'],
                                              lon=compute_service['Lon'], location_type=SlicerSDK.LocationType.EDGE)

    def __generate_experiment_bus_nodes(self):
        for trace_id, trace in self.traces.items():
            if trace == []: continue
            self.slicer_sdk.add_topology_node(label=f"bus_{trace_id}", service=self.bus_service, device=self.bus_device,
                                              networks=[self.slice_name], lat=trace[0]['Lat'],
                                              lon=trace[0]['Lon'])

    def __generate_experiment_RUs(self):
        for RU in self.RUs:
            self.slicer_sdk.add_RU_to_slice(self.slice_name, lat=RU['Lat'],
                                                       lon=RU['Lon'])
