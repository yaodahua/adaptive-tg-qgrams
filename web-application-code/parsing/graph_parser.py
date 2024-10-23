import numpy as np
import os
import re
from typing import List, cast
import pydot
import networkx as nx

import warnings

from utils.randomness_utils import RandomGenerator

# Suppress DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)


class GraphParser:
    def __init__(self, graph_dot_file: str):
        self.graph_dot_file = graph_dot_file
        assert os.path.exists(
            self.graph_dot_file
        ), f"File {self.graph_dot_file} does not exist"

        self.pydot_graph = self._parse(graph_dot_file=self.graph_dot_file)
        self.index_node = self._get_index_node(graph=self.pydot_graph)

        self.nx_graph = cast(nx.MultiDiGraph, nx.nx_pydot.from_pydot(self.pydot_graph))

        self.pydot_edges = [edge for edge in self.pydot_graph.get_edges()]
        self.edge_names = set(
            [
                re.search(
                    r"\w+", edge.get_attributes()["label"].replace('"', "")
                ).group(0)
                for edge in self.pydot_edges
            ]
        )

        self.pydot_map_edge_to_label = dict()
        self.pydot_map_label_to_edge = dict()

        for pydot_edge in self.pydot_edges:

            source = pydot_edge.get_source()
            destination = pydot_edge.get_destination()

            if (source, destination) not in self.pydot_map_edge_to_label:
                self.pydot_map_edge_to_label[(source, destination)] = []

            label = re.search(
                r"\w+", pydot_edge.get_attributes().get("label", None).replace('"', "")
            ).group(0)
            self.pydot_map_edge_to_label[(source, destination)].append(label)

            self.pydot_map_label_to_edge[label] = (source, destination)

        self.random_generator = RandomGenerator.get_instance()
        # print(self.pydot_map_label_to_edge)

    def get_edge_target(self, edge_name: str) -> str:
        return self.pydot_map_label_to_edge.get(edge_name)[1]

    def get_edge_source(self, edge_name: str) -> str:
        return self.pydot_map_label_to_edge.get(edge_name)[0]

    def get_edge_labels(self, source_node: str, target_node: str) -> List[str]:
        return self.pydot_map_edge_to_label.get((source_node, target_node))

    @staticmethod
    def _parse(graph_dot_file: str) -> pydot.Dot:

        graphs = pydot.graph_from_dot_file(graph_dot_file)
        graph = graphs[0]

        return graph

    @staticmethod
    def _get_index_node(graph: pydot.Dot) -> pydot.Node:
        index_nodes = list(
            filter(
                lambda x: x.get_attributes().get("label", None) == '"index"',
                graph.get_nodes(),
            )
        )
        assert len(index_nodes) == 1, f"Expected 1 index node, found {len(index_nodes)}"
        return index_nodes[0]

    def get_random_walk_from_index_to_target_edge(
        self, target_edge_name: str, max_length: int = 30
    ) -> List[str]:
        random_length = self.random_generator.rnd_state.randint(
            low=1, high=max_length + 1
        )
        walk = self.get_random_walk_fixed_length_from_index(length=random_length)
        source_node = self.get_edge_target(edge_name=walk[-1])
        target_node = self.get_edge_source(edge_name=target_edge_name)
        shortest_path = nx.shortest_path(
            self.nx_graph, source=source_node, target=target_node
        )

        for i in range(len(shortest_path) - 1):
            source_node = shortest_path[i]
            target_node = shortest_path[i + 1]
            edge_labels = self.get_edge_labels(
                source_node=source_node, target_node=target_node
            )
            assert edge_labels, f"No edge between {source_node} and {target_node}"
            walk.append(self.random_generator.rnd_state.choice(edge_labels))

        current_node = target_node
        target_node = self.get_edge_target(edge_name=target_edge_name)
        edge_labels = self.get_edge_labels(
            source_node=current_node, target_node=target_node
        )
        assert (
            target_edge_name in edge_labels
        ), f"Target edge {target_edge_name} not found"
        walk.append(target_edge_name)

        return walk

    def get_random_walk_fixed_length_from_index(self, length: int) -> List[str]:
        walk = []
        current_node = self.index_node.get_name()

        for _ in range(length):
            neighbors = list(self.nx_graph.neighbors(current_node))
            if not neighbors:
                break

            next_node = self.random_generator.rnd_state.choice(neighbors)
            edge_names = self.get_edge_labels(
                source_node=current_node, target_node=next_node
            )
            edge_name = self.random_generator.rnd_state.choice(edge_names)

            walk.append(edge_name)
            current_node = next_node

        return walk

    def get_random_walk_from_index_to_target_edge_(
        self, target_edge_name: str, max_length: int = 30
    ) -> List[str]:

        # expected_num_edges = len(
        #     list(filter(lambda x: target_edge_name == x, self.edge_names))
        # )
        # assert (
        #     expected_num_edges == 1
        # ), f"Expected one edge with name {target_edge_name} in graph, found {expected_num_edges}"

        walk = []

        walks = []
        while len(walk) > max_length or len(walk) == 0:
            walk = self._get_random_walk_from_index_to_target_edge(
                target_edge_name=target_edge_name
            )
            walks.append(walk)

        return walk

    def _get_random_walk_from_index_to_target_edge(
        self, target_edge_name: str
    ) -> List[str]:
        walk = []
        current_node = self.index_node.get_name()
        target_found = False

        while not target_found:
            neighbors = list(self.nx_graph.neighbors(current_node))

            if not neighbors:
                break

            next_node = self.random_generator.rnd_state.choice(neighbors)
            edge_names = self.get_edge_labels(
                source_node=current_node, target_node=next_node
            )
            edge_name = self.random_generator.rnd_state.choice(edge_names)

            walk.append(edge_name)
            current_node = next_node

            target_found = edge_name == target_edge_name

        assert target_found, f"Target edge {target_edge_name} not found"

        return walk


if __name__ == "__main__":
    app_name = "phoenix"
    graph_parser = GraphParser(graph_dot_file=f"graphs/{app_name}.txt")
    input_arguments = [
        re.search(r"\(.*\)", edge.get_attributes().get("label", None).replace('"', ""))
        .group(0)
        .replace("(", "")
        .replace(")", "")
        for edge in graph_parser.pydot_edges
    ]
    print(input_arguments)
    num_input_list = list(
        map(lambda x: len(x.split(",")) if x != "" else 0, input_arguments)
    )
    average_num_inputs = np.mean(num_input_list)
    print(f"Average number of inputs for {app_name}: {average_num_inputs}")
