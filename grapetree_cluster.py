import networkx as nx
import pandas as pd

import json
import argparse
from pathlib import Path
from copy import deepcopy
from operator import itemgetter


def arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument('input',
                        type=Path)

    parser.add_argument('output',
                        type=Path)

    return parser.parse_args()


def main():

    args = arguments()

    data = load_data(args.input)

    graph = build_graph(data)

    table = build_cluster_table(graph)

    write_out(table, args.output)


def load_data(data_path: Path):

    with data_path.open('r') as f:
        data = json.load(f)

    return data


def build_graph(data):

    graph = nx.Graph()
    for edge in data['links']:

        src = data['nodes'][edge['source']]
        dst = data['nodes'][edge['target']]
        dist = edge['distance']

        graph.add_node(src, strains=[])
        graph.add_node(dst, strains=[])
        graph.add_edge(src, dst, distance=dist)

    for strain, values in data['metadata'].items():

        node = values['__Node']

        try:
            graph.nodes[node]['strains'].append(strain)

        except KeyError:
            graph.nodes[node]['strains'] = [strain]

    return graph


def cluster_graph(original_graph, max_dist):

    graph = deepcopy(original_graph)

    to_remove = [(u, v)
                 for u, v, dist
                 in graph.edges.data('distance')
                 if dist > max_dist]

    graph.remove_edges_from(to_remove)

    clusters = enumerate(nx.connected_components(graph), 1)

    for cluster_number, cluster in clusters:

        for node in cluster:

            for strain in graph.nodes[node]['strains']:

                if not strain.startswith('_hypo') and strain != 'FILE':
                    yield strain, cluster_number


def build_cluster_table(graph):

    distances = sorted(set(edge[2] for edge in graph.edges.data('distance')))

    table = {}

    for d in distances:

        table[d] = {}

        for strain, clust_num in cluster_graph(graph, d):
            table[d][strain] = clust_num

    return pd.DataFrame(table)


def write_out(table: pd.DataFrame, outpath: Path):

    table.sort_values(table.columns[0])\
        .to_csv(outpath, sep='\t', index_label='genome')


if __name__ == '__main__':
    main()
