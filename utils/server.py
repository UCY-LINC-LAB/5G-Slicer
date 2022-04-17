import logging
from multiprocessing import Process

from flask import Flask, jsonify, request
from flask.views import MethodView
from networkx.readwrite import json_graph

from utils.general import CurrentEncoder

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


class NetworkAPI(MethodView):

    def get(self, network):
        if network is None:
            return jsonify({"networks": [key for key in self.slicerSDK.slices.keys()]})
        else:
            if network not in self.slicerSDK.slices:
                return jsonify({"error": "There is no network with that name"})
            else:
                res = json_graph.node_link_data(self.slicerSDK.slices[network].graph)
                return jsonify({"nodes": res.get("nodes", [])})


class NodeAPI(MethodView):

    def get(self, network, node_id):
        if network not in self.slicerSDK.slices:
            return {'error': 'network does not exist'}
        return jsonify(self.slicerSDK.slices[network].get_node_location(node_id))

    def post(self, network, node_id):
        lat = request.get_json().get('lat')
        lon = request.get_json().get('lon')
        return self.slicerSDK.move_node_to_location(network, node_id, lat, lon)


class APIService:

    class APIServiceException(Exception):
        pass

    def __init__(self, slicerSDK):
        self.slicerSDK = slicerSDK
        self.main_thread = None

    def start(self):
        if self.main_thread is not None:
            raise APIService.APIServiceException("The server is running")

        """
        server = Process(target=app.run)
        server.start()
        # ...
        server.terminate()
        server.join()
        """
        NodeAPI.slicerSDK = self.slicerSDK
        node_view = NodeAPI.as_view('node_api')
        NetworkAPI.slicerSDK = self.slicerSDK
        network_view = NetworkAPI.as_view('network_api')
        app = Flask(__name__)
        app.json_encoder = CurrentEncoder
        app.add_url_rule('/network/<network>', view_func=network_view, methods=['GET'])
        app.add_url_rule('/network/<network>/<node_id>', view_func=node_view, methods=['GET', 'POST'])

        def run_server(flask_app=None):
            flask_app.run(port=5555, host='0.0.0.0', debug=True, use_reloader=False)

        self.main_thread = Process(target=run_server, kwargs={'flask_app': app})
        self.main_thread.start()

    def stop(self):
        if self.main_thread is None: return
        self.main_thread.terminate()
        self.main_thread.join()
        self.main_thread = None
