#!/usr/bin/env python3

import jsonschema

networkcfg_json_schema = {
    "type": "object",
    "required": ["nodes", "communication_channels"],
    "properties": {
        "nodes": {
            "type": "array",
            "items": {"$ref": "#/definitions/node"}
        },
        "communication_channels": {
            "type": "array",
            "items": {"$ref": "#/definitions/channel"}
        }
    },
    "definitions": {
        "node": {
            "type": "object",
            "required": ["name", "path", "palcfg", "hardware", "deployment_type"],
            "properties": {
                "name": {"type": "string"},
                "path": {"type": "string"},
                "palcfg": {"type": "string"},
                "hardware": {"type": "string"},
                "deployment_type": {
                    "type": "string",
                    "enum": ["physical", "simulated", "mock"]
                }
            }
        },
        "channel": {
            "type": "object",
            "required": ["name", "connected_nodes", "channel_type"],
            "properties": {
                "name": {"type": "string"},
                "connected_nodes": {
                    "type": "array",
                    "items": {
                        "anyOf": [{"$ref": "#/definitions/can_node"},
                                  {"$ref": "#/definitions/uart_node"}]
                    }
                },
                "channel_type": {
                    "type": "string",
                    "enum": ["CAN", "UART"]
                },
                "communication_specification": {"type": "string"}
            }
        },
        "can_node": {
            "type": "object",
            "required": ["node", "can_port"],
            "properties": {
                "node": {"type": "string"},
                "can_port": {"type": "integer"}
            }
        },
        "uart_node": {
            "type": "object",
            "required": ["node", "port_type"],
            "properties": {
                "node": {"type": "string"},
                "port_type": {"enum": ["receiver", "transmitter"]}
            }
        }
    }
}

def valid(jsondoc):
    try:
        jsonschema.validate(instance=jsondoc, schema=networkcfg_json_schema)

    except jsonschema.exceptions.ValidationError as e:
        print("validating the networkconfig failed: " + e.message)
        return False

    return True
