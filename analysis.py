#!/usr/bin/env python3

import argparse
from collections import defaultdict
import csv
from enum import Enum, auto
import json
import networkconfig
import palconfig
import os
import sys
import typing

class Category(Enum):
    InterfaceInput = auto()
    InterfaceOutput = auto()
    Calibratable = auto()
    Displayable = auto()

    @staticmethod
    def fromString(s : str):
        if s == "Interface input":
            return Category.InterfaceInput
        elif s == "Interface output":
            return Category.InterfaceOutput
        elif s == "Calibratable":
            return Category.Calibratable
        elif s == "Displayable":
            return Category.Displayable
        else:
            raise TypeError('"{}" is not a valid Catergory'.format(s))

    def encode(self):
        return str(self)

    def __str__(self):
        if self == Category.InterfaceInput:
            return "Interface input"
        elif self == Category.InterfaceOutput:
            return "Interface output"
        elif self == Category.Calibratable:
            return "Calibratable"
        elif self == Category.Displayable:
            return "Displayable"

class Signal:
    def __init__(self, name : str, category: Category, datatype: str):
        self.name = name
        self.category = category
        self.datatype = datatype

    def encode(self):
        return self.__dict__

class LogicalNode:
    def __init__(self, name : str, signallist : list[Signal]):
        self.name = name
        self.signallist = signallist

    def encode(self):
        return self.__dict__

class PhysicalNode:
    def __init__(self, name :str, logicals: list[LogicalNode] = []):
        self.name = name
        self.logicals = logicals

    def encode(self):
        return self.__dict__

class CategoryCount:
    def __init__(self, name : str):
        self.name = name
        self.InterfaceInput = 0
        self.InterfaceOutput = 0
        self.Calibratable = 0
        self.Displayable = 0

    def encode(self):
        return self.__dict__

class DatatypeCount:
    def __init__(self, name : str):
        self.name = name
        self.countlist = defaultdict(int)

    def increment(self, datatype : str):
        # Increment the datatype
        self.countlist[datatype] += 1

    def encode(self):
        return self.__dict__

def getsignals(data_dictionaries):
    signallist = []
    for datadict in data_dictionaries:
        try:
            with open(datadict["file"], 'r', newline='') as csvfile:
                csvreader = csv.DictReader(csvfile)
                signallist.extend([Signal(row["Name"], Category.fromString(row["Type"]), row["Data type"]) for row in list(csvreader) if "//" not in row["Name"] and "" != row["Name"]])
        except FileNotFoundError as e:
            print("skipping paldd file: {}".format(datadict["file"]), file=sys.stderr)
    return signallist

def getcomponentdata(component):
    oldworkdir = os.getcwd()
    os.chdir(component["path"])
    signallist = []
    with open(component["config"], 'r') as f:
        jsonDoc = json.load(f)
        if not palconfig.valid(jsonDoc):
            exit(1)

        palconfigobj = palconfig.getpalconfig(jsonDoc)
        signallist.extend(getsignals(palconfigobj.data_dictionaries))
    os.chdir(oldworkdir)
    return LogicalNode(component["name"], signallist)

def parsephysicalnode(node):
    with open(node["path"] + "/" + node["palcfg"], 'r') as f:
        oldwdir = os.getcwd()
        os.chdir(node["path"])
        jsonDoc = json.load(f)
        if not palconfig.valid(jsonDoc):
            exit(1)

        logicals = []
        for logical in jsonDoc["components"]:
            logicals.append(getcomponentdata(logical))
        if jsonDoc["name"] == "ssc_secondary_es":
            logicals = [LogicalNode("ssc_secondary_es", getsignals(jsonDoc["data_dictionaries"]))]
        os.chdir(oldwdir)
        return PhysicalNode(jsonDoc["name"], logicals)

def joincentraldefinitions(nodedatainfo, centraldefinitions):
    for physicalnode in nodedatainfo:
        for node in physicalnode.logicals:
            for data in node.signallist:
                if data.datatype == "" :
                    for cd in centraldefinitions:
                        if cd["Name"] == data.name:
                            data.datatype = cd["Data type"]
                            break

def datatypesumperlogical(nodes):
    physicallist = list()
    for physicalnode in nodes:
        logicalcounts = []
        for logical in physicalnode.logicals:
            count = DatatypeCount(logical.name)
            for data in logical.signallist:
                count.increment(data.datatype)
            logicalcounts.append(count)
        physicallist.append(PhysicalNode(physicalnode.name, logicalcounts))
    return physicallist

def createsignaltable(physicalnodes) :
    signaltable = []
    for physical in physicalnodes:
        for logical in physical.logicals:
            for signal in logical.signallist:
                signaltable.append({"physicalname": physical.name, "logicalname": logical.name, "signalname": signal.name, "category": signal.category, "datatype" : signal.datatype})
    return signaltable

def logicallevelsum(signaltable, key):
    counts = []
    for signal in signaltable:
        if not any(d["physicalname"] == signal["physicalname"] and d["logicalname"] == signal["logicalname"] for d in counts):
            row = defaultdict(int)
            row["physicalname"] = signal["physicalname"]
            row["logicalname"] = signal["logicalname"]
            row[str(signal[key])] += 1
            counts.append(row)
        else :
            for row in (d for d in counts if d["physicalname"] == signal["physicalname"] and d["logicalname"] == signal["logicalname"]):
                # Should only be one item
                row[str(signal[key])] += 1
    return counts

def inputwithoutoutputs(signaltable):
    lonelyinputs = []
    for inputsignal in (s for s in signaltable if s["category"] == Category.InterfaceInput):
        if not any(s["category"] == Category.InterfaceOutput and s["signalname"] == inputsignal["signalname"] for s in signaltable):
            lonelyinputs.append(inputsignal)
    return lonelyinputs

def outputswithoutinputs(signaltable):
    lonelyoutputs = []
    for outputsignal in (s for s in signaltable if s["category"] == Category.InterfaceOutput):
        if not any(s["category"] == Category.InterfaceInput and s["signalname"] == outputsignal["signalname"] for s in signaltable):
            lonelyoutputs.append(outputsignal)
    return lonelyoutputs

def signalwithmorethanoneoutputsource(signaltable):
    print(hoi)

def calculatesignalconsumers(signaltable):
    outputs = filter(lambda signal: signal["category"] == Category.InterfaceOutput, signaltable)
    lonelyoutputs = outputswithoutinputs(signaltable)
    nonlonelyoutputs = filter(lambda signal: not any(signal["signalname"] == d["signalname"] and signal["category"] == Category.InterfaceOutput for d in lonelyoutputs), outputs)

    counts = []
    for outputsignal in nonlonelyoutputs:
        row = defaultdict(int)
        row["signalname"] = outputsignal["signalname"]

        for inputsignal in (i for i in signaltable if i["signalname"] == outputsignal["signalname"] and i["category"] == Category.InterfaceInput):
            if inputsignal["physicalname"] == outputsignal["physicalname"]:
                row["localconsumption"] += 1
            else:
                row["externalconsumption"] += 1

        counts.append(row)
    return counts

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="the main networkcfg file, relative to the vehicle directory")
    parser.add_argument("centraldefinitionsfile", help="the central definitions file, relative to the vehicle directory")
    args = parser.parse_args()

    oldwdir = os.getcwd()
    os.chdir("lyswe-vehicle")

    physicalnodes = []
    with open(args.inputfile, 'r') as f, open(args.centraldefinitionsfile, 'r') as centraldefinitionsfile:
        jsonDoc = json.load(f)
        # use jsonschema for validation
        if not networkconfig.valid(jsonDoc):
            print("invalid networkcfg file", file=sys.stderr)
            exit(1)

        for node in jsonDoc["nodes"]:
            if node["deployment_type"] == "physical":
                physicalnodes.append(parsephysicalnode(node))

        centraldefinitionsreader = csv.DictReader(centraldefinitionsfile)
        joincentraldefinitions(physicalnodes, list(centraldefinitionsreader))

    os.chdir(oldwdir)

    signaltable = createsignaltable(physicalnodes)

    with open("signaltable.json", "w") as f:
        f.write(json.dumps(signaltable, default=lambda o: o.encode(), indent=4))
    with open("categorysumperlogical.json", "w") as f:
        f.write(json.dumps(logicallevelsum(signaltable, "category"), default=lambda o: o.encode(), indent=4))
    with open("datatypesumperlogical.json", "w") as f:
        f.write(json.dumps(logicallevelsum(signaltable, "datatype"), default=lambda o: o.encode(), indent=4))
    with open("lonelyinputs.json", "w") as f:
        f.write(json.dumps(inputwithoutoutputs(signaltable), default=lambda o: o.encode(), indent=4))
    with open("lonelyoutputs.json", "w") as f:
        f.write(json.dumps(outputswithoutinputs(signaltable), default=lambda o: o.encode(), indent=4))
    with open("signalconsumercount.json", "w") as f:
        f.write(json.dumps(calculatesignalconsumers(signaltable), default=lambda o: o.encode(), indent=4))
