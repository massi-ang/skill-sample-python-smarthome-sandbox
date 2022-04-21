# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT
"""Device state implementation
"""

import typing
import json
import urllib
import logging
import os

from . import iot_data_aws

logger = logging.getLogger(__name__)

particle_device_url = os.getenv(
    "PARTICLE_DEVICE_URL", "https://z6qmvgzxac.execute-api.eu-west-1.amazonaws.com"
)

state = {}


def get_state(endpoint_id: str) -> typing.Dict[str, typing.Any]:
    """Get state
    """
    global state

    if not endpoint_id in state:
        try:
            res = iot_data_aws.get_thing_shadow(thingName=endpoint_id)
            shadow = json.loads(res["payload"].read())
            state[endpoint_id] = shadow["state"].get("desired", {})
        except Exception as ex:
            logger.error(ex)
    return state.get(endpoint_id, {})


def get_property_value(
    *,
    endpoint_id: str,
    property_name: str,
    instance: typing.Optional[str] = None,
    sku: str
) -> typing.Any:
    """Get a specific device property value
    """
    # Should replace with a prefix check
    if sku == "TS00-PARTICLE":
        result = (
            urllib.request.urlopen(particle_device_url + "/temp", data=None)
            .read()
            .decode("utf-8")
        )
        # TemperatureSensors report values in this format
        return {"value": json.loads(result)["temp"], "scale": "CELSIUS"}
    if sku == "LI00-PARTICLE":
        result = (
            urllib.request.urlopen(particle_device_url + "/light/state", data=None)
            .read()
            .decode("utf-8")
        )
        return "ON" if json.loads(result)["state"] == 1 else "OFF"
    if instance is not None:
        key = instance + "." + property_name
    endpoint_state = get_state(endpoint_id=endpoint_id)
    return endpoint_state.get(key, None)
