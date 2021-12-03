# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT
from os import strerror
import typing
import json
from . import iot_data_aws


def set_state(endpoint_id: str, identity: str, state: str) -> str:
    power_state_value = "ON" if state == "TurnOn" else "OFF"
    state_name = "powerState"
    msg = {"state": {"desired": {state_name: power_state_value}}}

    mqtt_msg = json.dumps(msg)
    response_update = iot_data_aws.update_thing_shadow(
        thingName=endpoint_id, payload=mqtt_msg.encode("utf8")
    )
    print("LOG device.power_controller.set_state -----")
    print(response_update)
    return power_state_value


def get_state(endpoint_id: str, identity: str) -> str:
    return "OFF"
