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

# Graph G contains palvar_read/palvar_write nodes, perform analysis
def find_pal_read_write_callgraphs(G):
    H = G.copy()
    H.remove_edges_from(nx.selfloop_edges(G))
    if not nx.is_directed_acyclic_graph(H):
        print('The graph was not a DAG, aborting analysis, the following cycles were found:')
        print(sorted(nx.simple_cycles(H)))
        return        
    
    callgraphs = []
    for node, nodeData in H.nodes(data=True):
        if any(x in nodeData['label'] for x in ['palvar_read', 'palvar_write']):
            chain = nx.subgraph(H, nx.ancestors(H, node) | {node})
            callgraphs.append([chain.nodes[n]['label'] for n in nx.topological_sort(chain)])

    callgraphs = [[node.replace("{","").replace('"', '').replace("}", '') for node in graph] for graph in callgraphs]

    return callgraphs


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
                'frequency' : 'tbd'
        }

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=dir_path, help='path to the folder containing compile_commands.json')
    parser.add_argument('physical', type=str, help='name of the analysed physical, for output purposes')
    args = parser.parse_args()
    
    # Create an output directory for this physical
    subprocess.run(['mkdir', '-p', './{}/build/'.format(args.physical), './{}/results/'.format(args.physical)])
    os.chdir('./{}/build'.format(args.physical))

    # Open compile_commands, transform each command to emit llvm bitcode
    with open(args.path + "/compile_commands.json", "r") as input:
        compile_commands = json.load(input)
        for file in compile_commands:
            file["command"] = change_command(file["command"]).replace('\\', '')
            cmd = file["command"].split()
            subprocess.run(cmd)
    
    # Link together the llvm bitcode
    subprocess.run('llvm-link -o app.ll *.ll', shell=True)

    # Use opt to generate a callgraph and use c++filt to demangle symbols
    subprocess.run(['opt', '-dot-callgraph', 'app.ll'])
    subprocess.run(['c++filt < app.ll.callgraph.dot > ../results/callgraph.dot'], shell=True)
    os.chdir('../results')

    G = nx.DiGraph(nx.nx_pydot.read_dot('callgraph.dot'))
    i=0
    callgraphs = []
    for components in nx.weakly_connected_components(G):
        subgraph = G.subgraph(components)
        nx.nx_pydot.write_dot(subgraph, 'subgraph{}.dot'.format(i))
        i = i + 1

        # Check if graph contains palvar_read or palvar_write nodes
        for k, v in subgraph.nodes(data="label"):
            if any(x in v for x in ['palvar_write', 'palvar_write']):
                nx.nx_pydot.write_dot(subgraph, 'palvar_graph{}.dot'.format(i))
                callgraphs = callgraphs +find_pal_read_write_callgraphs(subgraph)
                break

    with open('names_{}.csv'.format(args.physical), 'w', newline='') as csvfile, \
        open('graphs_{}.txt'.format(args.physical), 'w') as graphfile:
        fieldnames = ['type', 'variable', 'action', 'logical', 'physical', 'task', 'frequency']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in graph_to_row(callgraphs, args.physical):
            writer.writerow(row)
        for graph in callgraphs:
            graphfile.write('{}\n'.format(graph))