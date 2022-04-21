# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

from . import iot_aws
import typing


def list_endpoints(user_id: str) -> typing.Generator[str, None, None]:
    """Use the AWS IoT entries for state but get the discovery details from DynamoDB
    Wanted to list by group name but that requires a second lookup for the details
    iot_aws.list_things_in_thing_group(thingGroupName="Samples")
    """
    list_response = iot_aws.list_things()

    # Get a list of sample things by the user_id attribute
    for thing in list_response["things"]:
        if "user_id" in thing["attributes"]:
            if thing["attributes"]["user_id"] == user_id:
                yield thing["thingName"]  # We have an endpoint thing!
