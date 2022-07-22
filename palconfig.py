#!/usr/bin/env python3

import jsonschema
import typing

palcfg_json_schema = {
    "type": "object",
    "required": [
        "name",
        "project_code",
        "data_dictionaries",
        "tasks"
    ],
    "optional": [
        "components",
        "mutexes",
        "communication_ports",
        "ccp_settings",
        "uds_settings",
        "diagnostics_definitions",
        "can_interface"
    ],
    "properties": {
        "name": {"type": "string"},
        "project_code": {"type": "string"},
        "components": {
            "type": "array",
            "items": {"$ref": "#/definitions/component"}
        },
        "data_dictionaries": {
            "type": "array",
            "items": {"$ref": "#/definitions/data_dictionary"}
        },
        "build_variables": {
            "type": "array",
            "items": {"$ref": "#/definitions/build_variable"}
        },
        "tasks": {
            "type": "array",
            "items": {"$ref": "#/definitions/task"}
        },
        "mutexes": {
            "type": "array",
            "items": {"$ref": "#/definitions/mutex"}
        },
        "communication_ports": {
            "type": "object",
            "optional": ["can_ports", "uart_ports"],
            "properties": {
                "can_ports": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/can_port"}
                },
                "uart_ports": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/uart_port"}
                }
            }
        },
        "ccp_settings": {
            "type": "object",
            "required": ["cro", "dto", "station_address", "can_port_index"],
            "properties": {
                "cro": {"type": "string"},
                "dto": {"type": "string"},
                "station_address": {"type": "number"},
                "can_port_index": {"type": "number"}
            }

        },
        "uds_settings": {
            "type": "object",
            "required": ["can_tx_id", "can_rx_id", "can_func_rx_id",\
                "can_port_index"],
            "optional": ["can_tx_id_extd", "can_rx_id_extd"],
            "properties": {
                "can_tx_id": {"type": "string"},
                "can_rx_id": {"type": "string"},
                "can_func_rx_id": {"type": "string"},
                "can_port_index": {"type": "number"},
                "can_tx_id_extd": {"type": "string"},
                "can_rx_id_extd": {"type": "string"}
            }
        },
        "can_interface": {
            "type": "array",
            "items": {"$ref": "#/definitions/can_interface"}
        },
        "diagnostics_definitions": {
            "type": "array",
            "items": {"$ref": "#/definitions/diagnostics_definition"}
        }
    },
    "definitions": {
        "component": {
            "type": "object",
            "required": ["name", "path", "config"],
            "properties": {
                "name": {"type": "string"},
                "path": {"type": "string"},
                "config": {"type": "string"},
            }
        },
        "data_dictionary": {
            "type": "object",
            "required": ["file"],
            "properties": {
                "file": {"type": "string"},
            }
        },
        "build_variable": {
            "type": "object",
            "required": ["name", "value"],
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "string"},
            }
        },
        "can_port": {
            "type": "object",
            "required": ["baud_rate"],
            "properties": {
                "baud_rate": {"type": "number"},
            }
        },
        "uart_port": {
            "type": "object",
            "required": ["baud_rate"],
            "properties": {
                "baud_rate": {"type": "number"},
            }
        },
        "task": {
            "type": "object",
            "required": ["function_name", "period", "priority"],
            "properties": {
                "function_name": {"type": "string"},
                "period": {"type": "number"},
                "priority": {"type": "number"},
            }
        },
        "mutex": {
            "type": "object",
            "required": ["name", "tasks"],
            "properties": {
                "name": {"type": "string"},
                "tasks": {"type": "array"},
            }
        },
        "diagnostics_definition": {
            "type": "object",
            "required": ["file"],
            "properties": {
                "file": {"type": "string"},
            }
        },
        "can_interface": {
            "type": "object",
            "required": ["file", "node"],
            "properties": {
                "file": {"type": "string"},
                "node": {"type": "string"},
            }
        }
    }
}

def valid(jsondoc):
    try:
        jsonschema.validate(instance=jsondoc, schema=palcfg_json_schema)

    except jsonschema.exceptions.ValidationError as e:
        print("validating the networkconfig failed: " + e.message)
        return False

    return True

class PalConfig():
    def __init__(self, name : str, project_code:str, data_dictionaries : list[dict]):
        self.name = name
        self.project_code = project_code
        self.data_dictionaries = data_dictionaries

def getpalconfig(jsonDoc):
    return PalConfig(jsonDoc["name"], jsonDoc["project_code"], jsonDoc["data_dictionaries"])
