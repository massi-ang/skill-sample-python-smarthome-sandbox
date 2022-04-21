# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

import json
import boto3
from botocore.exceptions import ClientError
from endpoint_cloud.api_utils import ApiUtils

iot_aws = boto3.client("iot")


def create(endpoint_details):
    """Create the endpoint device your device implementation
    """
    return
    # thing_group_name_exists = check_thing_group_name_exists()
    # if not thing_group_name_exists:
    #     response = create_thing_group(samples_thing_group_name)
    #     if not ApiUtils.check_response(response):
    #         print('ERR api_handler_endpoint.create.create_thing_group.response', response)

    # Create the thing in AWS IoT
    response = create_thing(endpoint_details)
    if not ApiUtils.check_response(response):
        print("ERR api_handler_endpoint.create.create_thing.response", response)


def create_thing(endpoint_details):
    """Create a Thing in AWS IoT
    """
    print("LOG api_handler_endpoint.create_thing -----")
    # Create the ThingType if missing
    thing_type_name = create_thing_type(endpoint_details.sku)
    try:
        response = iot_aws.create_thing(
            thingName=endpoint_details.id,
            thingTypeName=thing_type_name,
            attributePayload={"attributes": {"user_id": endpoint_details.user_id}},
        )

        print(json.dumps(response))
        return response

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceAlreadyExistsException":
            print("WARN iot resource already exists, trying update")
            return update(endpoint_details)
    except Exception as e:
        print(e)
        return None

    # Add the thing to the Samples Thing Group
    # response = add_thing_to_thing_group(endpoint_details.id)
    # if not ApiUtils.check_response(response):
    #     print('ERR api_handler_endpoint.create.add_thing_to_thing_group.response', response)


def create_thing_group(thing_group_name):
    """Create a thing group in AWS IoT
    """
    print("LOG api_handler_endpoint.create_thing_group -----")
    response = iot_aws.create_thing_group(thingGroupName=thing_group_name)
    print(json.dumps(response))
    return response


# def add_thing_to_thing_group(thing_name):
#     response = iot_aws.add_thing_to_thing_group(thingGroupName=samples_thing_group_name, thingName=thing_name)
#     print('LOG api_handler_endpoint.add_thing_to_thing_group -----')
#     print(json.dumps(response))
#     return response


def create_thing_type(sku):
    print("LOG api_handler_endpoint.create_thing_type -----")
    # Set the default at OTHER (OT00)
    thing_type_name = "SampleOther"
    thing_type_description = "A sample endpoint"

    if sku.upper().startswith("LI"):
        thing_type_name = "SampleLight"
        thing_type_description = "A sample light endpoint"

    if sku.upper().startswith("MW"):
        thing_type_name = "SampleMicrowave"
        thing_type_description = "A sample microwave endpoint"

    if sku.upper().startswith("SW"):
        thing_type_name = "SampleSwitch"
        thing_type_description = "A sample switch endpoint"

    if sku.upper().startswith("TT"):
        thing_type_name = "SampleToaster"
        thing_type_description = "A sample toaster endpoint"

    response = {}
    try:
        response = iot_aws.create_thing_type(
            thingTypeName=thing_type_name,
            thingTypeProperties={"thingTypeDescription": thing_type_description},
        )
    except ClientError as e:
        print(e, e.response)

    print(json.dumps(response))
    return thing_type_name


def delete(endpoint_id):
    return
    # Delete from AWS IoT
    response = iot_aws.delete_thing(thingName=endpoint_id)
    print("LOG api_handler_endpoint.delete_thing.iot_aws.delete_item.response -----")
    print(response)
    return response


def update(endpoint_details):
    return
    # Create the ThingType if missing
    thing_type_name = create_thing_type(endpoint_details.sku)
    response = iot_aws.update_thing(
        thingName=endpoint_details.id,
        thingTypeName=thing_type_name,
        attributePayload={"attributes": {"user_id": endpoint_details.user_id}},
    )
    return response


def check_thing_group_name_exists():
    thing_groups = iot_aws.list_thing_groups(
        namePrefixFilter=samples_thing_group_name, recursive=False
    )
    if "thingGroups" in thing_groups:
        for thing_group in thing_groups["thingGroups"]:
            if thing_group["groupName"] == samples_thing_group_name:
                print("checkForThingGroup found", samples_thing_group_name)
                return True
    return False
