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

gwyrunnablestr ='''
    {name}: GatewayRunnable {{
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

    Vehicle_CAN : DataRouter {{
        parameters:
            busname = "Vehicle_CAN";
    }}
    PT_CAN : DataRouter {{
        parameters:
            busname = "PT_CAN";
    }}
    connections allowunconnected:
    {connections}

    safety_control_unit_primary_gwy_transmit_task.DataOut++ --> PT_CAN.in++;
    PT_CAN.out++ --> safety_control_unit_primary_gwy_receive_task.DataIn++;
    
    vehicle_control_unit_gwy_transmit_task.DataOut++ --> Vehicle_CAN.in++;
    Vehicle_CAN.out++ --> vehicle_control_unit_gwy_receive_task.DataIn++;
    
    central_gateway_gwy_transmit_task.DataOut++ --> Vehicle_CAN.in++;
    Vehicle_CAN.out++ --> central_gateway_gwy_receive_task.DataIn++;

    central_gateway_gwy_transmit_task.DataOut++ --> PT_CAN.in++;
    PT_CAN.out++ --> central_gateway_gwy_receive_task.DataIn++;
}}'''

def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)

def gateway_task(task):
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
        for row in reader:
            runnablename = '{}_{}'.format(row['physical'],row['task'])
            if gateway_task(row):
                runnables.add(gwyrunnablestr.format(name=runnablename, physical=row['physical'],
                            logical=row['logical'],task=row['task'],period=row['period (ms)']))
            else:
                runnables.add(runnablestr.format(name=runnablename, physical=row['physical'],
                            logical=row['logical'],task=row['task'],period=row['period (ms)']))
            if not row['variable'] in definitions:
                print(row['variable'])
                definitions[row['variable']] = ('Missing central_def', False)
            
            datadictname = '{}_{}'.format(row['physical'],row['variable'])
            relstr = 'true' if definitions[row['variable']][1] else 'false'
            typestr = definitions[row['variable']][0]
            datadicts.add(datadictstr.format(name=datadictname, datatype=typestr, reliability=relstr))
            
            if row['action'] == 'read':
                connections.append(readstr.format(runnable=runnablename, datadict=datadictname))
            elif row['action'] == 'write':
                connections.append(writestr.format(runnable=runnablename, datadict=datadictname))

        outfile.write(filestr.format(runnables='\n'.join(runnables), datadicts='\n\t'.join(datadicts),
                        connections='\n\t'.join(connections)))