# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

import typing

import json

from botocore.exceptions import ClientError

from . import iot_data_aws


def set_state(endpoint_id: str, instance: str, op: str) -> str:
    """Implement this method to actuate the directive on your device"""

    # Convert to a local stored state
    toggle_state_value = "OFF" if op == "TurnOff" else "ON"

    # Send the state to the Thing Shadow
    state_name = instance + ".toggleState"
    msg = {"state": {"desired": {state_name: toggle_state_value}}}
    mqtt_msg = json.dumps(msg)

    response_update = iot_data_aws.update_thing_shadow(
        thingName=endpoint_id, payload=mqtt_msg.encode("utf8")
    )
    print("LOG device.toggle_controller.set_state -----")
    print(response_update)
    return toggle_state_value


def get_state(endpoint_id: str, instance: str) -> str:
    reported_state = 0
    try:
        response = iot_data_aws.get_thing_shadow(thingName=endpoint_id)
        payload = json.loads(response["payload"].read())
        reported_state = payload["state"]["reported"][instance + ".toggleState"]
        print("LOG device.toggle_controller.get_state:", reported_state)

    except ClientError as e:
        print(e)
    except KeyError as errorKey:
        print("Could not find key:", errorKey)
    return reported_state
