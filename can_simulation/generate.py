#!/usr/bin/env python3
import argparse
import cantools
import csv
import json
import os

datadictTemplate = '''dd[{index}].name = "{name}";'''

logicalTemplate = '''logical[{index}].name = "{name}";
        logical[{index}].priority = 6;
        logical[{index}].period = ;
        logical[{index}].canInput = FiCo4OMNeT::CanList{{definition: {canIn}}};
        logical[{index}].canOutput = FiCo4OMNeT::CanList{{definition: {canOut}}};
        logical[{index}].dataDictOut = FiCo4OMNeT::DataDictList{{definition: {ddOutputs} }};
        '''

physicalTemplate = '''package fico4omnet.examplesLy.LYES;

import fico4omnet.nodes.can.LyPhysicalNode;
import fico4omnet.operatingsystem.DataDictionary;

module {node} extends LyPhysicalNode {{
    parameters:
        numDataDicts = {numDataDicts};
        numLogicals = {numLogicals};
        sinkApp.priority = 14 + ;
		//Source app has default prio of 4

        {dataDicts}

        {logical}
    connections allowunconnected:
        {connections}
}}'''

getTemplate = '''logical[{logical}].getDataDict++ <--> dd[{datadict}].get++;'''
setTemplate = '''logical[{logical}].setDataDict++ --> dd[{datadict}].set;'''

def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)

# Lists containing the CAN input and outputs for the physical nodes
SCUCANInput = []
SCUCANOutput = []
CGWCANInput = []
CGWCANOutput = []
VCUCANInput = []
VCUCANOutput = []

# Lists and dicts for internal node connections
runnablesCGW = set()
datadictsCGW = set()
connectionsCGW = []

runnablesSCU = set()
datadictsSCU = set()
connectionsSCU = []

runnablesVCU = set()
datadictsVCU = set()
connectionsVCU = []

def nodeHasDD(node, name):
    if node == "SCU":
        return name in datadictsSCU
    elif node == "CGW":
        return name in datadictsCGW
    elif node == "VCU":
        return name in datadictsVCU
    else:
        print("oops, illegal node in nodeHasDD")
        return False

def addForwardingDD(node, name):
    if node == "SCU":
        datadictsSCU.add(name)
        connectionsSCU.append(('get', 'gwy_transmit_task', name))
        connectionsSCU.append(('set', 'gwy_receive_task', name))
        print("SCU forwarding" + name)
    elif node == "CGW":
        datadictsCGW.add(name)
        connectionsCGW.append(('get', 'gwy_transmit_task', name))
        connectionsCGW.append(('set', 'gwy_receive_task', name))
        print("CGW forwarding" + name)
    elif node == "VCU":
        datadictsVCU.add(name)
        connectionsVCU.append(('get', 'gwy_transmit_task', name))
        connectionsVCU.append(('set', 'gwy_receive_task', name))
        print("VCU forwarding" + name)
    else:
        print("oops, illegal node in addForwardingDD")
        
def toNedMessage(message, node, bus):
    nedMessage = {}
    nedMessage['canID'] = message.frame_id
    nedMessage['sizeInBytes'] = message.length
    nedMessage['bus'] = bus
    
    dds=[]
    for signal in message.signals:
        dd = {}
        if signal.name.endswith("_upd"):
            #ignore the update counter, just increment the size of the base signal by 2
            continue
        elif signal.name.endswith("_rel"):
            # The reliability signal, rename to _reliable
            name = "{}iable".format(signal.name)
            dd['ddName'] = name
            dd['bitSize'] = signal.length

            # Check whether the signal already exists as a dd for that node, if not add it
            if not nodeHasDD(node, name):
                # This signal is a forwarding signal, add it to the physical and connect the rx/tx
                # logicals
                addForwardingDD(node, name)
        else:
            # The normal signal, increment its size by 2 bits to account for the _upd signal
            dd['ddName'] = signal.name
            dd['bitSize'] = signal.length + 2

            # Check whether the signal already exists as a dd for that node, if not add it
            if not nodeHasDD(node, signal.name):
                # This signal is a forwarding signal, add it to the physical and connect the rx/tx
                # logicals
                addForwardingDD(node, signal.name)
        dds.append(dd)
    nedMessage['dd'] = dds
    return nedMessage

def addOutput(message, node, bus):
    nedMessage = toNedMessage(message, node, bus)

    if node == "SCU":
        SCUCANOutput.append(nedMessage)
    elif node == "VCU":
        VCUCANOutput.append(nedMessage)
    elif node == "CGW":
        CGWCANOutput.append(nedMessage)
    else:
        print("unknown node")
    

def addInput(message, node, bus):
    nedMessage = toNedMessage(message, node, bus)

    if node == "SCU":
        SCUCANInput.append(nedMessage)
    elif node == "VCU":
        VCUCANInput.append(nedMessage)
    elif node == "CGW":
        CGWCANInput.append(nedMessage)
    else:
        print("unknown node")

def parseDBC(file):
    dbc = cantools.database.load_file(file)
    for message in dbc.messages:
        if 'scup_PT' in message.name:
            addOutput(message, "SCU", "powertrain")
            addInput(message, "CGW", "powertrain")
        elif 'cgw_PT' in message.name:
            addOutput(message, "CGW", "powertrain")
            addInput(message, "SCU", "powertrain")
        elif 'cgw_Veh' in message.name:
            addOutput(message, "CGW", "vehicle")
            addInput(message, "VCU", "vehicle")
        elif 'vcu_Veh' in message.name:
            addOutput(message, "VCU", "vehicle")
            addInput(message, "CGW", "vehicle")
        elif 'vcu_Sol' in message.name:
            addOutput(message, "VCU", "solar")
        elif 'cgw_Tel' in message.name:
            addOutput(message, "CGW", "telematics")
        else:
            print("Node/Bus combination not detected: " + message.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=file_path, help='path to the csv network file, can be absolute or relative')
    parser.add_argument('centraldef', type=file_path, help='path to central.definitions file, can be relative or absolute')
    parser.add_argument('fulldbc', type=file_path, help='path to gwy_full.dbc file, can be relative or absolute')
    args = parser.parse_args()
    file = args.path

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
                 'i_ivi_closures_lock_t':32}

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

    # print(definitions)

    with open(file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        # Figure out which logicals and datadicts exist in each physical and whether they write/read
        for row in reader:
            if row['physical'] == 'safety_control_unit_primary':
                runnablesSCU.add(row['task'])
                datadictsSCU.add(row['variable'])
                
                if row['action'] == 'read':
                    connectionsSCU.append(('get', row['task'], row['variable']))
                else:
                    connectionsSCU.append(('set', row['task'], row['variable']))
            elif row['physical'] == 'central_gateway':
                runnablesCGW.add(row['task'])
                datadictsCGW.add(row['variable'])
                
                if row['action'] == 'read':
                    connectionsCGW.append(('get', row['task'], row['variable']))
                else:
                    connectionsCGW.append(('set', row['task'], row['variable']))
            elif row['physical'] == 'vehicle_control_unit':
                runnablesVCU.add(row['task'])
                datadictsVCU.add(row['variable'])
                
                if row['action'] == 'read':
                    connectionsVCU.append(('get', row['task'], row['variable']))
                else:
                    connectionsVCU.append(('set', row['task'], row['variable']))
            else:
                print("oopsie")

    parseDBC(args.fulldbc)

    with open('SCUNode.ned', 'w') as scuFile:
        runnables = list(runnablesSCU)
        runnables.append("psc_background_app")
        runnables.append("propulsion_safety_10ms")
        runnableDict = {}
        for run in runnables:
            runnableDict[run] = []
            
        datadicts = list(datadictsSCU)
        
        connections = []
        for (action, task, dd) in connectionsSCU:
            runnableIndex = runnables.index(task)
            ddIndex = datadicts.index(dd)
            if action == "get":
                connections.append(getTemplate.format(logical=runnableIndex, datadict=ddIndex))
            else:
                connections.append(setTemplate.format(logical=runnableIndex, datadict=ddIndex))
                runnableDict[task].append({'ddName': dd, 'bitSize' : datatypes[definitions[dd][0]]})
        
        scuFile.write(physicalTemplate.format(node='SCUNode', numDataDicts=len(datadicts), 
                                                numLogicals=len(runnables),
                                                dataDicts='\n\t\t'.join(
                                                    [datadictTemplate.format(index=datadicts.index(dd), name=dd) for dd in datadicts]),
                                                logical='\n\t\t'.join(
                                                    [logicalTemplate.format(
                                                        index=runnables.index(run) , 
                                                        name=run,
                                                        canIn= json.dumps(SCUCANInput) if run == "gwy_receive_task" else [],
                                                        canOut= json.dumps(SCUCANOutput) if run == "gwy_transmit_task" else [],
                                                        ddOutputs=json.dumps(runnableDict[run])
                                                    ) for run in runnables]),
                                                connections='\n\t\t'.join(connections)
                                            ))
        
    with open('CGWNode.ned', 'w') as cgwFile:
        runnables = list(runnablesCGW)
        runnables.append("psc_background_app")
        runnables.append("gw_fw_upgrade_forwarding_task")
        runnableDict = {}
        for run in runnables:
            runnableDict[run] = []
        datadicts = list(datadictsCGW)
        
        connections = []

        for (action, task, dd) in connectionsCGW:
            runnableIndex = runnables.index(task)
            ddIndex = datadicts.index(dd)
            if action == "get":
                connections.append(getTemplate.format(logical=runnableIndex, datadict=ddIndex))
            else:
                connections.append(setTemplate.format(logical=runnableIndex, datadict=ddIndex))
                runnableDict[task].append({'ddName': dd, 'bitSize': datatypes[definitions[dd][0]]})
        
        cgwFile.write(physicalTemplate.format(node='CGWNode', numDataDicts=len(datadicts), 
                                                numLogicals=len(runnables),
                                                dataDicts='\n\t\t'.join(
                                                    [datadictTemplate.format(index=datadicts.index(dd), name=dd) for dd in datadicts]),
                                                logical='\n\t\t'.join(
                                                    [logicalTemplate.format(
                                                        index=runnables.index(run) , 
                                                        name=run,
                                                        canIn= json.dumps(CGWCANInput) if run == "gwy_receive_task" else [],
                                                        canOut= json.dumps(CGWCANOutput) if run == "gwy_transmit_task" else [],
                                                        ddOutputs=json.dumps(runnableDict[run])
                                                        ) for run in runnables]),
                                                connections='\n\t\t'.join(connections)
                                            ))

    with open('VCUNode.ned', 'w') as vcuFile:
        runnables = list(runnablesVCU)
        runnables.append("psc_background_app")
        runnables.append("dcm_vcu_10_ms_task")
        runnables.append("tms_100ms_task")
        runnableDict = {}
        for run in runnables:
            runnableDict[run] = []
        
        datadicts = list(datadictsVCU)
        
        connections = []

        for (action, task, dd) in connectionsVCU:
            runnableIndex = runnables.index(task)
            ddIndex = datadicts.index(dd)
            if action == "get":
                connections.append(getTemplate.format(logical=runnableIndex, datadict=ddIndex))
            else:
                connections.append(setTemplate.format(logical=runnableIndex, datadict=ddIndex))
                runnableDict[task].append({'ddName': dd, 'bitSize' : datatypes[definitions[dd][0]]})
        
        vcuFile.write(physicalTemplate.format(node='VCUNode', numDataDicts=len(datadicts), 
                                                numLogicals=len(runnables),
                                                dataDicts='\n\t\t'.join(
                                                    [datadictTemplate.format(index=datadicts.index(dd), name=dd) for dd in datadicts]),
                                                logical='\n\t\t'.join(
                                                    [logicalTemplate.format(
                                                        index=runnables.index(run) , 
                                                        name=run,
                                                        canIn= json.dumps(VCUCANInput) if run == "gwy_receive_task" else [],
                                                        canOut= json.dumps(VCUCANOutput) if run == "gwy_transmit_task" else [],
                                                        ddOutputs=json.dumps(runnableDict[run])
                                                        ) for run in runnables]),
                                                connections='\n\t\t'.join(connections)
                                            ))