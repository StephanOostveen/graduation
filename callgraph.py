#!/usr/bin/env python3
import json
import re
import argparse
import os
import subprocess
import networkx as nx
import csv
import re
# Change the compile command to only do preprocessing and compilation (-S)
# and emit llvm bitcode (-emit-llvm) and change the output file location (-o ...)
def change_command(command):
    emit_llvm = re.sub('=lld','=lld -S -emit-llvm', command)
    return re.sub('-o CMa[\S/]+','', emit_llvm)

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def add_dot_labels(graph):
    for node in graph:
        graph.nodes[node]['shape']= 'box'
        if 'palvar_read' in graph.nodes[node]['label']:
            graph.nodes[node]['fillcolor'] = '#77AADD'
            graph.nodes[node]['style'] = 'filled'
        elif 'palvar_write' in graph.nodes[node]['label']:
            graph.nodes[node]['fillcolor'] = '#BBCC33'
            graph.nodes[node]['style'] = 'filled'

        c = graph.nodes[node].get('fillcolor')
        if len(nx.ancestors(graph, node)) == 0 and c:   
            graph.nodes[node]['fillcolor'] = "{}:{}".format(c, '#EE8866')
            graph.nodes[node]['style'] = 'striped'
        elif len(nx.ancestors(graph, node)) == 0:
            graph.nodes[node]['fillcolor'] = '#EE8866'
            graph.nodes[node]['style'] = 'filled'

def anonymize_graph(graph):
    for node in graph:
        if 'palvar_read' in graph.nodes[node]['label']:
            graph.nodes[node]['label'] = 'read_variable_x'
        elif 'palvar_write' in graph.nodes[node]['label']:
            graph.nodes[node]['label'] = 'write_variable_x'
        elif len(nx.ancestors(graph, node)) == 0:
            graph.nodes[node]['label'] = 'task'
        else:
            graph.nodes[node]['label'] = 'function_y'

# Graph G contains palvar_read/palvar_write nodes, perform analysis
def find_pal_read_write_callgraphs(G):
    H = G.copy()
    print("\t\tFound and removed the following selfloops: {}".format(list(nx.selfloop_edges(G))))
    H.remove_edges_from(nx.selfloop_edges(G))
    if not nx.is_directed_acyclic_graph(H):
        print('\t\tThe graph was not a DAG, aborting analysis, the following cycles were found:')
        print(sorted(nx.simple_cycles(H)))
        return
    reducedGraph = nx.DiGraph(overlap='false', layout='sfdp')
    anonymizedGraph = nx.DiGraph(overlap='false', layout='sfdp')

    for node in H:
        H.nodes[node]['label'] = H.nodes[node]['label'].replace("{","").replace('"', '').replace("}", '')

    callgraphs = []
    for node, nodeData in H.nodes(data=True):
        if any(x in nodeData['label'] for x in ['palvar_read', 'palvar_write']):
            chain = nx.subgraph(H, nx.ancestors(H, node) | {node})
            reducedGraph.update(chain)
            anonymizedGraph.update(chain)
            callgraphs.append([chain.nodes[n]['label'] for n in nx.topological_sort(chain)])

    callgraphs = [[node.replace("{","").replace('"', '').replace("}", '') for node in graph] for graph in callgraphs]

    add_dot_labels(reducedGraph)
    add_dot_labels(anonymizedGraph)
    anonymize_graph(anonymizedGraph)
    return (callgraphs, reducedGraph, anonymizedGraph)


def graph_to_row(callgraphlist, physical):
    for callgraph in callgraphlist:
        #  fieldnames = ['variable', 'action', 'logical', 'physical', 'task', 'frequency']
        palfunc = callgraph[-1]
        task = callgraph[0]

        palfunc_re = re.match("(palvar_write|palvar_read)_(\w+)", palfunc)
        task_re = re.match("(\w+)", task)

        if not palfunc_re or not task_re:
            print("Had issues parsing callgraph: {}".format(callgraph))
            continue
        action = 'write' if palfunc_re.group(1) == 'palvar_write' else 'read'
        variable = palfunc_re.group(2)
        task_name = task_re.group(1)

        yield { 'type' : 'paldd',
                'variable' : variable,
                'action' : action,
                'logical' : 'tbd',
                'physical' : physical,
                'task' : task_name,
                'period (ms)' : 'tbd'
        }

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=dir_path, help='path to the folder containing compile_commands.json')
    parser.add_argument('physical', type=str, help='name of the analysed physical, for output purposes')
    args = parser.parse_args()
    print("----------------{}----------------".format("Starting code transformation"))
    # Create an output directory for this physical
    print("{}....".format("Creating build and results folder"))
    subprocess.run(['mkdir', '-p', './{}/build/'.format(args.physical), './{}/results/'.format(args.physical)])
    print("{}....".format("Changing directory to build folder"))
    os.chdir('./{}/build'.format(args.physical))
    if os.listdir("."):
        raise RuntimeError("Build directory was not empty, clean it first")
    # Open compile_commands, transform each command to emit llvm bitcode
    print("{}....".format("Open compile_commands.json"))
    with open(args.path + "/compile_commands.json", "r") as input:
        compile_commands = json.load(input)
        print("{}....".format("Executing compile commands"))
        for file in compile_commands:
            file["command"] = change_command(file["command"]).replace('\\', '')
            cmd = file["command"].split()
            subprocess.run(cmd)
    
    # Link together the llvm bitcode
    print("{}....".format("Linking together the LLVM-IR files"))
    subprocess.run('llvm-link -o app.ll *.ll', shell=True)

    # Use opt to generate a callgraph and use c++filt to demangle symbols
    print("{}....".format("Outputing callgraph in dot"))
    subprocess.run(['opt', '-dot-callgraph', 'app.ll'])
    print("{}....".format("Demangling C++ symbols and printing result to ../results/callgraph.dot"))
    subprocess.run(['c++filt < app.ll.callgraph.dot > ../results/callgraph.dot'], shell=True)
    os.chdir('../results')
    
    print("----------------{}----------------".format("Starting callgraph analysis"))
    G = nx.DiGraph(nx.nx_pydot.read_dot('callgraph.dot'))
    i=0
    callgraphs = []
    print("{}....".format("Separate weakly connected components"))
    for components in nx.weakly_connected_components(G):
        subgraph = G.subgraph(components)
        nx.nx_pydot.write_dot(subgraph, 'subgraph{}.dot'.format(i))
        
        # Check if graph contains palvar_read or palvar_write nodes
        print("{}....".format("\tSearch for relevant nodes in weakly connected component {}".format({i})))
        for k, v in subgraph.nodes(data="label"):
            if any(x in v for x in ['palvar_read', 'palvar_write']):
                print("{}....".format("\t\tFound relevant node, create callgraph for each relevant node"))
                nx.nx_pydot.write_dot(subgraph, 'palvar_graph{}.dot'.format(i))
                callList, reducedGraph, anonymizedGraph = find_pal_read_write_callgraphs(subgraph)
                nx.nx_agraph.write_dot(reducedGraph, 'palvar_reduced_graph{}.dot'.format(i))
                nx.nx_agraph.write_dot(anonymizedGraph, 'palvar_anon_graph{}.dot'.format(i))
                callgraphs = callgraphs + callList
                break
        i = i + 1
    
    print("----------------{}----------------".format("Create resulting CSV"))
    with open('names_{}.csv'.format(args.physical), 'w', newline='') as csvfile, \
        open('graphs_{}.txt'.format(args.physical), 'w') as graphfile:
        fieldnames = ['type', 'variable', 'action', 'logical', 'physical', 'task', 'period (ms)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in graph_to_row(callgraphs, args.physical):
            writer.writerow(row)
        for graph in callgraphs:
            graphfile.write('{}\n'.format(graph))