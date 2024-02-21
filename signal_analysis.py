#!/usr/bin/env python3

import argparse
import json
import os
import csv
import pprint
import itertools
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

definitions = {}
datatypes = {'i_gear_t' : 32, 
            'i_safe_ramp_state_t': 32, 
            'i_safe_vehicle_motion_t': 32,
            'i_safe_boolean_t': 32,
            'i_hecu_op_mode_t': 32,
            'i_esc_err_t': 32,
            'i_light_blinking_request_t': 32,
            'float': 32,
            'i_vehicle_state_t': 32,
            'i_power_mode_t': 32,
            'uint16_t': 16,
            'i_on_off_t': 32,
            'i_ivi_avh_enable_t': 32,
            'i_charger_state_t': 32,
            'i_hecu_epb_act_req_t': 32,
            'i_wiper_position_t': 32,
            'int32_t': 32,
            'i_hecu_prnd_t': 32,
            'int8_t': 8,
            'i_operating_mode_dt_t': 32,
            'i_regen_control_request_t': 32,
            'i_actual_avh_status_t': 32,
            'Data type': 0,
            'i_switch_state_t': 32,
            'int16_t': 16,
            'i_ivi_regen_intensity_t': 32,
            'i_alarm_hazard_lights_t': 32,
            'i_safe_sig_cnd_t': 32,
            'bool': 8,
            'i_hecu_avh_fail_t': 32,
            'i_ccu_hlc_fsm_state_t': 32,
            'i_speed_func_selection_t': 32,
            'uint32_t':32,
            'uint8_t':8,
            'i_ivi_closures_lock_t':32
            }

def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)

def type_summation(file):
    with open(file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        variables = set()
        for row in reader:
            variables.add(row['variable'])
        
        typeCount = {}
        counter = 0
        for variable in variables:
            counter += 1
            datatype = definitions[variable][0]
            if datatype in typeCount:
                typeCount[datatype] += 1
            else:
                typeCount[datatype] = 1
        print("counter: " + str(counter))
        print(typeCount)
        print("typecount sum: " + str(sum(typeCount.values())))

def read_write_ratio(file):
    pp = pprint.PrettyPrinter(indent=4)
    with open(file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        ratios = {}
        count = 0;
        skipcount=0
        for row in reader:
            if row['task'] in  ["gwy_receive_task", "gwy_transmit_task"]:
                skipcount +=1
                continue
            count +=1
            name = row['variable']
            if name in ratios:
                read, write = ratios[name]
                if row['action'] == 'read':
                    ratios[name] = (read+1, write)
                else:
                    ratios[name] = (read, write+1)
            else:
                if row['action'] == 'read':
                    ratios[name] = (1,0)
                else:
                    ratios[name] = (0,1)
        print("(read,write)")
        for key, group in itertools.groupby(sorted(ratios.items(), key = lambda x : x[1]), lambda x: x[1]):
            print(key, ": ", sum(1 for _ in group))
        # pp.pprint(ratios)
        print("sc ", skipcount)
        print ("count: ", count)

def rate_table(file):
    table = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
    index = ['1', '10', '50', '100', '500']
    pp = pprint.PrettyPrinter(indent=4)
    with open(file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        skipcount=0

        producers = {}
        consumers = []
        for row in reader:
            if row['task'] in  ["gwy_receive_task", "gwy_transmit_task"]:
                skipcount +=1
                continue
            count +=1
            if row['action'] == 'write':
                producers[row['variable']] = index.index(row['period (ms)'])
            else:
                consumers.append((row['variable'], index.index(row['period (ms)'])))
        nf = 0
        for variable, c_index in consumers:
            p_index = producers.get(variable)
            if p_index:
                table[p_index][c_index] += 1
            else:
                nf += 1
        print(table)
        print("not found: ", nf)

def get_communication_type(producer, consumer):
    if producer == consumer:
        return 'local'
    elif producer == 'safety_control_unit_primary' and consumer == 'central_gateway':
        return 'direct'
    elif producer == 'safety_control_unit_primary' and consumer == 'vehicle_control_unit':
        return 'bridged'
    elif producer == 'central_gateway':
        return 'direct'
    elif producer == 'vehicle_control_unit' and consumer == 'central_gateway':
        return 'direct'
    elif producer == 'vehicle_control_unit' and consumer == 'safety_control_unit_primary':
        return 'bridged'
    else:
        print("oopsiedoodle")
        return 'oopsiedoodle'
def communication_type(file):
    # Get the #local, #direct, #bridged 
    producers = {} # {var: physical}
    consumers = [] #[(var, physical)]
    comm_type = {} # {var: {local: 5, direct:7, bridged: 42}}
    
    with open(file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['task'] in  ["gwy_receive_task", "gwy_transmit_task"]:
                continue
            if row['action'] == 'write':
                producers[row['variable']] = row['physical']
            else:
                consumers.append((row['variable'], row['physical']))
    
    print(len(producers.keys()))
    for variable, physical_consumer in consumers:
        if variable not in producers:
            continue
        
        communication = get_communication_type(producers[variable], physical_consumer)
        if variable in comm_type:
            comm_type[variable][communication] += 1
        else:
            comm_type[variable] = {'local':0, 'direct': 0, 'bridged': 0, 'oopsiedoodle': 0}
            comm_type[variable][communication] += 1
    local = 0
    direct = 0
    bridged = 0
    local_direct = 0
    local_bridged = 0
    direct_bridged = 0
    all = 0
    error = 0
    count = 0
    for name, counts in comm_type.items():
        count += 1
        if counts['local'] != 0 and counts['direct'] == 0 and counts['bridged'] == 0:
            local += 1
        elif counts['direct'] != 0 and counts['local'] == 0 and counts['bridged'] == 0:
            direct += 1
        elif counts['bridged'] != 0 and counts['direct'] == 0 and counts['local'] == 0:
            bridged += 1
        elif counts['local'] != 0 and counts['direct'] != 0 and counts['bridged'] == 0:
            local_direct += 1
        elif counts['local'] != 0 and counts['direct'] == 0 and counts['bridged'] != 0:
            local_bridged += 1
        elif counts['local'] == 0 and counts['direct'] != 0 and counts['bridged'] != 0:
            direct_bridged += 1
        elif counts['local'] != 0 and counts['direct'] != 0 and counts['bridged'] != 0:
            all += 1
        else:
            error +=1
            print("error for ", name)
        if counts['oopsiedoodle'] != 0:
            error +=1
            print("Thingamabob forgot to Majig the Thinga resulting in ", counts['oopsiedoodle'], ' oopsiedoodles for ', name)
   
    print("local: ", local)
    print("direct: ", direct)
    print("bridged: ", bridged)
    print("local_direct: ", local_direct)
    print("local_bridged: ", local_bridged)
    print("direct_bridged", direct_bridged)
    print("all: ", all)
    print("error: ", error)

def set_size(width_pt, fraction=1, subplots=(1, 1)):
    """Set figure dimensions to sit nicely in our document.

    Parameters
    ----------
    width_pt: float
            Document width in points
    fraction: float, optional
            Fraction of the width which you wish the figure to occupy
    subplots: array-like, optional
            The number of rows and columns of subplots.
    Returns
    -------
    fig_dim: tuple
            Dimensions of figure in inches
    """
    # Width of figure (in pts)
    fig_width_pt = width_pt * fraction
    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    golden_ratio = (5**.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio * (subplots[0] / subplots[1])

    return (fig_width_in, fig_height_in)


def produced_consumed_runnable(file):
    runnable = {} #{runnable_name : {read: 4, write: 2}}

    with open(file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = '{}_{}'.format(row['task'], row['physical'])
            if name in runnable:
                runnable[name][row['action']] += 1
            else:
                runnable[name] = {'read': 0, 'write': 0}
                runnable[name][row['action']] += 1

    runnable_list = list(runnable.items())

    fig, ax = plt.subplots(1,1,figsize=set_size(0.95*424.58624))
    
    plt.grid(visible=True, alpha=0.7)
    plt.scatter([r[1]['write'] for r in runnable_list if 'gwy' in r[0]], 
                [r[1]['read'] for r in runnable_list if 'gwy' in r[0]], 
                c='tab:orange', marker='.', label='CAN runnable')
    plt.scatter([r[1]['write'] for r in runnable_list if 'gwy' not in r[0]], 
                [r[1]['read'] for r in runnable_list if 'gwy' not in r[0]], 
                c='tab:blue', marker='.', label='Other runnable')
    plt.xlabel('Nr of produced data dictionaries')
    plt.ylabel('Nr of consumed data dictionaries')
    plt.legend()
    plt.title('Data dictionaries consumed/produced per runnable')
    plt.rcParams.update({"font.family": "serif",  # use serif/main font for text elements
    "text.usetex": True,     # use inline math for ticks
    "pgf.rcfonts": False     # don't setup fonts from rc parameters
    })
    fig.tight_layout()
    fig.savefig('paper/images/Produce_Consume_graph.pgf', format='pgf')
    plt.show()

def produced_consumed_can(file):
    runnable = {} #{runnable_name: {'read': 4, 'write':5}}

    with open(file, 'r') as jsonfile:
        jsonarray = json.load(jsonfile)
        for r in jsonarray:
            name = '{}_{}'.format(r['physical'], r['name'])
            if name in runnable:
                print('oops')
            runnable[name] = {'read': len(r['canIn']), 'write': len(r['canOut'])}
    
    runnable_list = list(runnable.items())

    fig, ax = plt.subplots(1,1,figsize=set_size(0.95*424.58624))
    plt.grid(visible=True, alpha=0.7)
    plt.scatter([r[1]['write'] for r in runnable_list if not any(node in r[0] for node in ['cgw', 'SCU', 'VCU'])],
                [r[1]['read'] for r in runnable_list if not any(node in r[0] for node in ['cgw', 'SCU', 'VCU'])],
                c='tab:purple', marker='.', label='Parametrizable end nodes')
    plt.scatter([r[1]['write'] for r in runnable_list if 'gwy' in r[0]], 
                [r[1]['read'] for r in runnable_list if 'gwy' in r[0]], 
                c='tab:orange', marker='.', label='CAN runnable')
    plt.scatter([r[1]['write'] for r in runnable_list if 'gwy' not in r[0] and any(node in r[0] for node in ['cgw', 'SCU', 'VCU'])], 
                [r[1]['read'] for r in runnable_list if 'gwy' not in r[0] and any(node in r[0] for node in ['cgw', 'SCU', 'VCU'])], 
                c='tab:blue', marker='.', label='Other Runnable')
    
    plt.xlabel('Nr of produced CAN messages')
    plt.ylabel('Nr of consumed CAN messages')
    plt.legend()
    plt.title('CAN messages consumed/produced')
    plt.rcParams.update({"font.family": "serif",  # use serif/main font for text elements
    "text.usetex": True,     # use inline math for ticks
    "pgf.rcfonts": False     # don't setup fonts from rc parameters
    })
    fig.tight_layout()
    fig.savefig('paper/images/Produce_Consume_CAN_graph.pgf', format='pgf')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=file_path, help='path to the csv network file, can be absolute or relative')
    parser.add_argument('centraldef', type=file_path, help='path to central.definitions file, can be relative or absolute')
    parser.add_argument('canjson', type=file_path)
    args = parser.parse_args()
    file = args.path

    # Create a lookup dictionary of central definitions of the Datadictionaries
    with open(args.centraldef, 'r', newline='') as central_definitions:
        reader = csv.DictReader(central_definitions)
        for row in reader:
            if row['With reliability'] == 'Yes':
                # With reliability there are two datadicts generated, so add both
                name = '{}_reliable'.format(row['Name'])
                definitions[row['Name']] = (row['Data type'], True)
                definitions[name] = (row['Data type'], True)
            else:
                definitions[row['Name']] = (row['Data type'], False)

    type_summation(file)
    read_write_ratio(file)
    rate_table(file)
    communication_type(file)
    produced_consumed_runnable(file)
    # produced_consumed_can(args.canjson)