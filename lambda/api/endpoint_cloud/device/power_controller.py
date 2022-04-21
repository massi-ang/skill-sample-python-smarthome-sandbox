# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT
from os import strerror
import typing
import json
from . import iot_data_aws
import urllib
import os
import logging

logger = logging.getLogger(__name__)

particle_device_url = os.getenv(
    "PARTICLE_DEVICE_URL", "https://z6qmvgzxac.execute-api.eu-west-1.amazonaws.com"
)


def set_state(*, endpoint_id: str, state: str, sku: str) -> str:
    # My device specific implementation based on SKU

    if sku == "LI00-PARTICLE":
        url = particle_device_url + "/light"
        # My device takes values 'on' and 'off'
        request = urllib.request.Request(
            url,
            data=json.dumps({"action": state.lower()}).encode("utf8"),
            headers={"content-type": "application/json"},
        )
        result = urllib.request.urlopen(request).read().decode("utf-8")
        if result == "OK":
            return state

    state_name = "powerState"
    msg = {"state": {"desired": {state_name: state}}}

    mqtt_msg = json.dumps(msg)
    response_update = iot_data_aws.update_thing_shadow(
        thingName=endpoint_id, payload=mqtt_msg.encode("utf8")
    )
    logger.info("device.power_controller.set_state -----")
    logger.info(response_update)
    return state
