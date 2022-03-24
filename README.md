# 5G-Slicer
*5G-Slicer: An emulator for mobile IoT applications deployed over 5G network slices*


Experimentation with 
5G-enabled services over network slices is extremely challenging as it requires the 
deployment and coordination of numerous physical devices, including
edge and cloud resources.
To alleviate the difficulties in setting up real-world 5G testbeds, 
we introduce 5G-Slicer extension of the [Fogify framework](https://github.com/UCY-LINC-LAB/fogify). 
5G-Slicer facilitates the definition of mobile network slices 
through modeling abstractions for radio units, mobile nodes, trajectories, etc., 
while also offering realistic network QoS by dynamically altering -at runtime- signal strength. 
Moreover, 5G-Slicer provides an already realized scenario for a city-scale deployment that 
smart-city researchers can simply configure through a "ready-to-use" template, 
leaving 5G-Slicer responsible for translating it into an emulated environment. </p>

---
## System Overview

A typical deployment starts by either describing the application services and network fabric via the 5G-Slicer model 
specification or by parameterizing a "ready-to-use" testbed template. 
The model specification can denote a wide range of network slice parameters, including the position of compute nodes and RUs, 
network links and their QoS, mobile node traces, communication protocols and VNFs applicable on nodes. 
On the contrary, parametrizable use-case templates automatically produce 5G deployments for IoT applications. 
The output of each template is a programming view equivalent to a validated deployment description. 
The topology and trajectories are propagated to the control layer.

Then, the system extracts from the description the network slice specification
and any signal degradation models defined during the modeling process. 
With these, it produces an in-memory Network Conceptual Graph (NCG), which contains the aforementioned information 
and will be used by the system for the runtime state propagation during the experimentation. 
The graph nodes represent network and compute devices annotated with information about their capabilities and 
deployed services, while edges denote the links between the nodes.
The weight of each edge is determined by network QoS, incl. data rate, network delay, packet and error rate. 
Then 5G-Slicer translates the NCG to an emulated environment by utilizing the Fogify Emulator Connector. 

The connector is responsible for the emulation environment instantiation, and the deployment of the IoT application  through the FogifySDK. 
Furthermore, the Trajectory Manager parses the traces and applies the updates on the NCG, 
and, in turn propagates these to the running emulated environment.
One can view through an interactive map the traces of mobile nodes, 
their performance (i.e. cpu, energy), and the load imposed to MECs. 

## Features

### 5G Slicing Modeling

5G-Slicer offers high-level modeling abstractions that capture the key characteristics of a 5G network slice along with the mobility of network entities. The model's expressivity enables users to design and build complex 5G network slices, encapsulating QoS definition, user-plane network functions, physical components, such as access points and base stations, physical nodes' positioning and trajectories, new network technologies (multi-user MIMO and beam-forming), and virtualized MEC and Cloud resources.

### Positioning & Mobility

5G-Slicer seamlessly "translates" the high-level 5G slicing description to a running emulated environment. 
At runtime, 5G-Slicer alters the positions of the mobile entities based on the described trajectories, and, consequently,
based on entities' positioning, alters at runtime the respective network QoS link quality, such as network latency,  bandwidth,  error rate,  etc.  

### ITS Use case template

5G-Slicer provides a "ready-to-use" template for a city-scale transportation sector that users are able to introduce their services. Specifically, users simply introduce the smart bus network testbed via the template that utilizes real-world mobility data from the [Dublin smart city project](https://data.smartdublin.ie). In this, buses continuously report their locations and other attributes (i.e., environment conditions) to a central ITS to perform location-based analytic tasks (i.e., bus delay reporting), in collaboration with employed MECs that act as local data aggregators and are placed nearby bus stops.

### Monitoring Capabilities

5G-Slicer provides a wide-range of monitoring utilization metrics that captured 
from the deployed 5G-enabled application, such as CPU utilization, occupied memory size, network and disk I/O traffic. 
Moreover, users can extract application-level metrics to the emulator. 
Finally, the system introduced new monitoring capabilities for packet-level monitoring and analytics to the emulation suite.


## Documentation
You will find the full documentation of the Fogify at the [documentation page](https://ucy-linc-lab.github.io/fogify/5g-slicer.html).
At Fogify's documentation, we provide details about installation, modeling, experimentation, and, generally, a full get-started guide about the project. 


## Publications

For more details about 5G-Slicer and our scientific contributions, you can read the papers of [5G-Slicer](http://linc.ucy.ac.cy/index.php?id=12) 
and a published [Demo](http://linc.ucy.ac.cy/index.php?id=12).
If you would like to use 5G-Slicer for your research, you should include at least on of the following BibTeX entries. 

5G-Slicer's paper BibTeX citation:
```
@INPROCEEDINGS{Symeonides2022,
author    = {Symeonides, Moysis and Trihinas, Demetris and Pallis, George and Dikaiakos, Marios D. and Psomas, Constantinos and Krikidis, Ioannis},
title     = {5G-Slicer: An emulator for mobile IoT applications deployed over 5G network slices}, 
booktitle = {Proceedings of the 7th ACM/IEEE Conference on Internet of Things Design and Implementation},
year      = {2022}
series    = {IoTDI ’22}
}
```

5G-Slicer's demo BibTeX citation:
```
@inproceedings{Symeonides2020,
author    = {Symeonides, Moysis and Trihinas, Demetris and Pallis, George and Dikaiakos, Marios D.},
title     = {Demo: Emulating 5G-Ready Mobile IoT Services},
booktitle = {Proceedings of the 7th ACM/IEEE Conference on Internet of Things Design and Implementation}, 
year      = {2022}
series    = {IoTDI ’22}
} 
```


## Acknowledgements

This work is partially supported by the EU Commission through [RAINBOW](https://rainbow-h2020.eu/)  871403 (ICT-15-2019-2020) project 
and by the Cyprus Research and Innovation Foundation through COMPLEMENTARY/0916/0916/0171 and INFRASTRUCTURES/1216/0017 (IRIDA) projects. 
The authors wish to thank Dr. Christos Tranoris and prof. Spyros Denazis of the U. of Patras for providing measurements from the "Patras 5G" testbed, 
which was supported by the 5GVINNI H2020 (EU grant agreement No. 815279)


## License
The framework is open-sourced under the Apache 2.0 License base. The codebase of the framework is maintained by the authors for academic research and is therefore provided "as is".
