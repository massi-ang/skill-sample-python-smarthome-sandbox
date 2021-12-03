# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT
'''
'''
from . import iot_data_aws
import typing
import json

def get_state(endpoint_id: str) -> typing.Dict[str, typing.Any]:
    state = {}
    try:
        res = iot_data_aws.get_thing_shadow(thingName=endpoint_id)
        shadow = json.loads(res["payload"].read())
        state = shadow["state"].get("desired", {})
    except Exception as e:
        print("LOG ", e)
    return state