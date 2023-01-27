#!/usr/bin/env python3
import argparse
import csv
import os
runnablestr ='''
    {name}: Runnable {{
        parameters:
            physical = "{physical}";
            logical = "{logical}";
            task = "{task}";
            period = {period};
    }}'''

datadictstr = '''{name} : DataDictionary {{
    parameters:
        datatype = "{datatype}";
        reliability = {reliability};
    }}'''

readstr = '''{runnable}.InterfaceInput++ <--> {datadict}.get++;'''

writestr = '''{runnable}.InterfaceOutput++ --> {{@display("ls=green,2");}} --> {datadict}.set;'''

filestr = '''network vehicle {{
    submodules:
    {runnables}

    {datadicts}

    connections allowunconnected:
    {connections}
}}'''

def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)

def not_gateway_task(task):
    return not task['task'] in ['gwy_receive_task', 'gwy_transmit_task']

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=file_path, help='path to the csv network file, can be absolute or relative')
    parser.add_argument('centraldef', type=file_path, help='path to central.definitions file, can be relative or absolute')
    args = parser.parse_args()
    file = args.path
    # script is called from build folder context by cmake
    if not os.path.isfile(file):
        raise FileNotFoundError(file)

    runnables = set()
    datadicts = set()
    connections = []

    definitions = {}

    with open(args.centraldef, 'r', newline='') as central_definitions:
        reader = csv.DictReader(central_definitions)
        for row in reader:
            if row['With reliability'] == 'Yes':
                name = '{}_reliable'.format(row['Name'])
                definitions[row['Name']] = (row['Data type'], True)
                definitions[name] = (row['Data type'], True)
            else:
                definitions[row['Name']] = (row['Data type'], False)

    with open(file, 'r', newline='') as csvfile, open('sim.ned', 'w') as outfile:
        reader = csv.DictReader(csvfile)
        for row in filter(not_gateway_task, reader):
            runnablename = '{}_{}'.format(row['physical'],row['task'])
            runnables.add(runnablestr.format(name=runnablename, physical=row['physical'],
                                logical=row['logical'],task=row['task'],period=row['period (ms)']))
            if not row['variable'] in definitions:
                print(row['variable'])
                definitions[row['variable']] = ('Missing central_def', False)
            
            datadicts.add(datadictstr.format(name=row['variable'], datatype=definitions[row['variable']][0], reliability= 'true' if definitions[row['variable']][1] else 'false'))
            if row['action'] == 'read':
                connections.append(readstr.format(runnable=runnablename, datadict=row['variable']))
            elif row['action'] == 'write':
                connections.append(writestr.format(runnable=runnablename, datadict=row['variable']))
        outfile.write(filestr.format(runnables='\n'.join(runnables), datadicts='\n\t'.join(datadicts),
                        connections='\n\t'.join(connections)))