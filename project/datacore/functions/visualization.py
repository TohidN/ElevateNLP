import matplotlib.pyplot as plt
import networkx as nx
from datacore.components import POS, RELATION
from datacore.models import Concept, Relation
from django.conf import settings

"""
Note: to get node data try
print(graph.nodes.data(data=True))
"""


def get_component_color(component):
    # Generates colors from one of `datacore.components` lists
    n = len(component)
    relation_colors = {}
    cmap = plt.cm.get_cmap("hsv", n)
    for i in range(n):
        relation_colors[component[i][0]] = cmap(i)
    return relation_colors


def draw_graph(graph, path="", name="graph.png", layout="spring_layout"):
    graph_attribute_color = get_component_color(POS)
    graph_edge_color = get_component_color(RELATION)
    # for concept in concepts:
    # 	graph.nodes[concept.id]['attribute'] = concept.attribute
    # 	graph.nodes[concept.id]['color'] = graph_attribute_color[concept.attribute]
    # f = plt.figure(figsize=[12, 10])
    f = plt.figure(figsize=[6 + len(graph.nodes), 4 + len(graph.nodes)])

    # for full layout documentation visit: https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout
    if layout == "spring_layout":
        pos = nx.spring_layout(graph, k=1, iterations=20)
    elif layout == "shell_layout":
        pos = nx.shell_layout(graph)
    elif layout == "spiral_layout":
        pos = nx.spiral_layout(graph)
    elif layout == "circular_layout":
        pos = nx.circular_layout(graph)
    elif layout == "planar_layout":
        pos = nx.planar_layout(graph)
    else:
        raise Exception("Please enter a valid NetworkX layout.")

    plt.axis("off")
    for node in graph.nodes:
        graph.nodes[node]["color"] = graph_attribute_color[
            graph.nodes[node]["attribute"]
        ]

    nx.draw_networkx_labels(
        graph,
        pos=pos,
        font_size=9,
        labels={key: value for (key, value) in graph.nodes.data("title")},
    )
    for key in graph_edge_color:
        nx.draw_networkx_edges(
            graph,
            pos=pos,
            edge_color=graph_edge_color[key],
            edgelist=list(
                [x[0], x[1]] for x in graph.edges.data() if x[2]["type"] == key
            ),
        )

    nx.draw_networkx_edge_labels(
        graph,
        pos=pos,
        font_size=9,
        edge_labels={(x, y): value for (x, y, value) in graph.edges.data("title")},
    )
    for key in graph_attribute_color:
        nx.draw_networkx_nodes(
            graph,
            pos=pos,
            edgecolors="#AAAAAA",
            node_color=graph_attribute_color[key],
            nodelist=list(
                x[0]
                for x in graph.nodes().data()
                if x[1]["color"] == graph_attribute_color[key]
            ),
        )

    import os

    if not os.path.exists(path):
        os.makedirs(path)
    f.savefig(os.path.join(path, name))

    # Close figure and plot to release memory
    f.clf()
    plt.close("all")
    # plt.close()


def get_component_title(type):
    from datacore.components import RELATION

    for relation in RELATION:
        if relation[0] == type:
            return relation[1]


def get_direct_relations(id):
    relations = Relation.objects.filter(concepts__contains=[id])
    return relations


def get_direct_hierarchy_relations(id):
    relations = Relation.objects.filter(
        concepts__contains=[id], relation_type="HYPONYM"
    )
    return relations


def get_direct_relations_graph(id):
    graph = nx.MultiDiGraph()
    # add all nodes and edges(id only)
    relations = get_direct_relations(id)

    # 'relationship_choices' is removed as a variable and is added to Component
    # TODO: expand using http://www.unlweb.net/wiki/Universal_Relations
    for rel in relations:
        graph.add_edge(
            int(rel.concepts[0]),
            int(rel.concepts[1]),
            type=rel.relation_type,
            title=get_component_title(rel.relation_type),
        )
    concepts = list(
        Concept.objects.filter(id__in=[key for key, value in graph.nodes.data()])
    )  # query
    for concept in concepts:
        graph.nodes[concept.id]["title"] = concept.get_title()
        graph.nodes[concept.id]["attribute"] = concept.pos
    return graph


def get_hierarchy_relations_graph(id):
    graph = nx.MultiDiGraph()
    pkids = [id]
    newpkids = []
    ongoing = True
    while ongoing:
        if pkids:
            for pkid in pkids:
                relations = get_direct_hierarchy_relations(pkid)
                ongoing = False
                for rel in relations:
                    if pkid == rel.concepts[0]:  # or pkid == rel.concepts[1]:
                        graph.add_edge(
                            rel.concepts[0],
                            rel.concepts[1],
                            type=rel.relation_type,
                            title=get_component_title(rel.relation_type),
                        )
                        newpkids.append(rel.concepts[1])
                        ongoing = True
            pkids = newpkids
            newpkids = []

    concepts = list(
        Concept.objects.filter(id__in=[key for key, value in graph.nodes.data()])
    )  # query
    for concept in concepts:
        graph.nodes[concept.id]["title"] = concept.get_title()
        graph.nodes[concept.id]["attribute"] = concept.pos
    return graph


def get_neighborhood_relations_graph(id, n=1):
    graph = nx.MultiDiGraph()
    pkids = []
    pkids.append(id)
    newpkids = []
    oldpkids = []
    while n > 0:
        if pkids:
            for pkid in pkids:
                if pkid not in oldpkids:
                    oldpkids.append(pkid)
                    newpkids = []
                    concept = Concept.objects.get(id=pkid)
                    relations = get_direct_relations(pkid)
                    for rel in relations:
                        graph.add_edge(
                            int(rel.concepts[0]),
                            int(rel.concepts[1]),
                            type=rel.relation_type,
                            title=get_component_title(rel.relation_type),
                        )
                        if int(rel.concepts[0]) not in oldpkids:
                            newpkids.append(int(rel.concepts[0]))
                        if int(rel.concepts[1]) not in oldpkids:
                            newpkids.append(int(rel.concepts[1]))
        pkids = newpkids
        n = n - 1

    concepts = list(
        Concept.objects.filter(id__in=[key for key, value in graph.nodes.data()])
    )  # query
    for concept in concepts:
        graph.nodes[concept.id]["title"] = concept.get_title()
        graph.nodes[concept.id]["attribute"] = concept.pos
    return graph


def generate_relation_graph(id):
    graph = get_direct_relations_graph(int(id))
    draw_graph(
        graph, f"{settings.MEDIA_ROOT}/concept/{id}/", "relation.png", "spring_layout"
    )


def generate_hierarchy_graph(id):
    graph = get_hierarchy_relations_graph(int(id))
    draw_graph(
        graph, f"{settings.MEDIA_ROOT}/concept/{id}/", "hierarchy.png", "shell_layout"
    )


def generate_neighborhood_graph(id, n=2):
    graph = get_neighborhood_relations_graph(int(id), n)
    draw_graph(
        graph,
        f"{settings.MEDIA_ROOT}/concept/{id}/",
        "neighborhood.png",
        "planar_layout",
    )
