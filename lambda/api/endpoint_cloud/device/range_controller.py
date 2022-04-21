# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT
import typing

from botocore.exceptions import ClientError
import json
from . import iot_data_aws


def set_value(endpoint_id: str, instance: str, value: float) -> None:
    """Implement this method to actuate the directive on your device"""

    # Update the Thing Shadow
    msg = {"state": {"desired": {}}}
    # NOTE: The instance is used to keep the stored value unique
    msg["state"]["desired"][instance + ".rangeValue"] = value
    mqtt_msg = json.dumps(msg)
    response_update = iot_data_aws.update_thing_shadow(
        thingName=endpoint_id, payload=mqtt_msg.encode("utf8")
    )
    print("LOG api_handler_directive.process.range_controller.response_update -----")
    print(response_update)


def get_value(endpoint_id: str, instance: str) -> float:
    """Implement this method to retrieve the current value"""

    reported_range_value = 0
    try:
        response = iot_data_aws.get_thing_shadow(thingName=endpoint_id)
        payload = json.loads(response["payload"].read())
        reported_range_value = payload["state"]["reported"][instance + ".rangeValue"]
        print(
            "LOG api_handler_directive.process.range_controller.range_value:",
            reported_range_value,
        )

    except ClientError as e:
        print(e)
    except KeyError as errorKey:
        print("Could not find key:", errorKey)
    return reported_range_value
