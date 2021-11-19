import numpy as np
import networkx as nx
from tqdm import tqdm


def rule_1(daily_sequences_list):
    print ("Function 'rule_1()' starts!")
    # Associate nodes according to Rule 1
    for daily_sequence in tqdm(daily_sequences_list):
        if daily_sequence:
            # Transform the reportviews.NodeView data type to list
            node_list = list(daily_sequence.nodes())
            for i in range(1, len(node_list)):
                day_of_seq = daily_sequences_list.index(daily_sequence)
                current_seq = daily_sequences_list[day_of_seq]
                current_seq.add_edge(node_list[i-1], node_list[i], EdgeType=1, weight=1)
    print ("All nodes in sequence graphs are associated into sequences!")
    return daily_sequences_list

def rule_23(daily_sequences_list, day_delta):
    # 同一个host按照顺序
    # 同一个host按照同一种类型
    print ("Function 'rule_23()' starts!")

    # Associate nodes according to Rule 2 and Rule 3
    # list of day_delta daily sequences >> tuple{H:[node numbers]}
    H_tuple_list = [None]*day_delta
    # list of day_delta daily sequences >> tuple{H:tuple} >> tuple{A:[node numbers]}
    A_tuple_list = [None]*day_delta

    for daily_sequence in tqdm(daily_sequences_list):
        if daily_sequence:
            # key: H;    value: list of nodes number
            H_record_tuple = {}
            node_list = list(daily_sequence.nodes())
            for node_i in node_list:
                current_H = daily_sequence.nodes[node_i]['H']
                if current_H not in H_record_tuple.keys():
                    H_record_tuple[current_H] = [node_i]
                else:
                    # 同host按照时间顺序的上一个节点和当前节点的连接
                    node_j = H_record_tuple[current_H][-1]
                    daily_sequence.add_edge(node_j, node_i, EdgeType=2, weight=1)
                    H_record_tuple[current_H].append(node_i)

            A_record_tuple_tuple = {}
            # key represents H
            for key in H_record_tuple:
                # Nodes in H_list have the same H
                H_list = H_record_tuple[key]
                A_record_tuple = {}
                for node_i in H_list:
                    current_A = daily_sequence.nodes[node_i]['A']
                    if current_A not in A_record_tuple.keys():
                        A_record_tuple[current_A] = [node_i]
                    else:
                        # 同一种host下按照时间顺序，同一种操作type连接
                        node_j = A_record_tuple[current_A][-1]
                        daily_sequence.add_edge(node_j, node_i, EdgeType=3, weight=1)
                        A_record_tuple[current_A].append(node_i)

                A_record_tuple_tuple[key]=A_record_tuple

            day_of_seq = daily_sequences_list.index(daily_sequence)
            H_tuple_list[day_of_seq] = H_record_tuple
            A_tuple_list[day_of_seq] = A_record_tuple_tuple


    print ("Edges are added based on rule2 and rule3 in daily sequence!")
    return daily_sequences_list, H_tuple_list, A_tuple_list

# 同一个用户之间不同天之间操作之间的关系
def rule_456(daily_sequences_list, H_tuple_list, A_tuple_list, day_delta):
    print ("Function 'rule_456()' starts!")

    # Associate daily sequences according to Rule 4
    graph = nx.MultiGraph()

    # Add all daily sequences to the graph
    for daily_sequence in daily_sequences_list:
        if daily_sequence:                                                                                                                                                                  
            graph = nx.compose(graph,daily_sequence)

    # Add edges between daily sequences
    for i in range(0, day_delta):
        for j in range(i+1, day_delta):
            if daily_sequences_list[i] and daily_sequences_list[j]:
                node_list_i = list(daily_sequences_list[i].nodes())
                node_list_j = list(daily_sequences_list[j].nodes())
                u1 = node_list_i[0]
                v1 = node_list_j[0]

                u2 = node_list_i[-1]
                v2 = node_list_j[-1]

                len_u = len(node_list_i)
                len_v = len(node_list_j)

                # weight
                weight_u_v = len_u / len_v if len_u < len_v else len_v / len_u

                w = round(weight_u_v,3)

                # 不同天之间，开始和结尾的节点相连，rule4
                graph.add_edge(u1, v1, EdgeType=4, weight=w)
                graph.add_edge(u2, v2, EdgeType=4, weight=w)

                # Add edges based on Rule 5 and Rule 6
                # key represents H
                for key in H_tuple_list[i]:
                    if key in H_tuple_list[j].keys():
                        # 某天某host下的开始和结尾节点之间相连
                        u1 = H_tuple_list[i][key][0]
                        v1 = H_tuple_list[j][key][0]
                        u2 = H_tuple_list[i][key][-1]
                        v2 = H_tuple_list[j][key][-1]
                        len_u = len(H_tuple_list[i][key])
                        len_v = len(H_tuple_list[j][key])
                        weight_u_v = len_u / len_v if len_u < len_v else len_v / len_u
                        w = round(weight_u_v, 3)
                        graph.add_edge(u1, v1, EdgeType=5, weight=w)
                        graph.add_edge(u2, v2, EdgeType=5, weight=w)

                        for operation_type in A_tuple_list[i][key]:
                            if operation_type in A_tuple_list[j][key]:
                                # 某天某个host下某种操作开始和结束节点之间的关联
                                u1 = A_tuple_list[i][key][operation_type][0]
                                v1 = A_tuple_list[j][key][operation_type][0]
                                u2 = A_tuple_list[i][key][operation_type][-1]
                                v2 = A_tuple_list[j][key][operation_type][-1]
                                len_u = len(A_tuple_list[i][key][operation_type])
                                len_v = len(A_tuple_list[j][key][operation_type])
                                weight_u_v = len_u / len_v if len_u < len_v else len_v / len_u
                                w = round(weight_u_v, 3)
                                graph.add_edge(u1, v1, EdgeType=6, weight=w)
                                graph.add_edge(u2, v2, EdgeType=6, weight=w)

    return graph
