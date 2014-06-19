topology-builder
================

The package includes simple topology scheduler
The information about the topology is loaded within the yaml-syntax description files. There are a pair of files: for nodes and adges.
With the help of python-network we allow to draw the loaded graph and check it.
There is a tool for generating the traffic. It generates the packets which are mapped to the bandwidth.
The bandwidth is accumulated as statistics on the edges.

After it was done - we launch the schedule process.
There are some preparations. They include:
1) Make adjacency matrix.
2) Launch the Dijkstra algorithm for it. We get shortest routes and distances.
3) Combine the route information and accumulated edge weights (traffic statistics) to produce the informative distance between nodes.
4) Creating the task as the list of pairs: (<node>,<priority>)
5) Combine it into one list of nodes and priorities

Then we launch the very simple scheduler which iterates through compute nodes and topology and sums the distance the important nodes with coefficients equal to the priority of this nodes.
