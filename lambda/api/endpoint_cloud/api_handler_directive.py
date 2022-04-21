# -*- coding: utf-8 -*-

# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file except in
# compliance with the License. A copy of the License is located at
#
#    http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.
"""This module

"""
import json
import typing
import logging
import os
import boto3

from alexa.skills.smarthome import AlexaResponse
from jsonschema import validate, SchemaError, ValidationError



from endpoint_cloud.controllers import (
    AlexaRangeController,
    AlexaToggleController,
    AlexaPowerController,
    AlexaCookingController,
    AlexaAuthorization,
    AlexaStateController,
)
from endpoint_cloud.device import discovery

from .api_auth import ApiAuth
from .api_handler_endpoint import ApiHandlerEndpoint

# Customized implementation

logger = logging.getLogger(__name__)

dynamodb_aws = boto3.resource("dynamodb")
iot_aws = boto3.client("iot")
iot_data_aws = boto3.client("iot-data")


ENDPOINT_DETAILS_TABLE = os.getenv("ENDPOINT_DETAILS_TABLE", "EndpointDetails")
USERS_TABLE = os.getenv("USERS_TABLE", "Users")

endpoint_details_table = dynamodb_aws.Table(ENDPOINT_DETAILS_TABLE)


class ApiHandlerDirective:
    """Handler for Alexa Directives"""

    def process(
        self, request, client_id, client_secret, redirect_uri
    ) -> typing.Dict[str, any]:
        logger.info("api_handler_directive.process -----")
        # print(json.dumps(request))

        response = None
        # Process an Alexa directive and route to the right namespace
        # Only process if there is an actual body to process otherwise return an ErrorResponse

        # Temperature sensors cannot be controlled, hence they will never be target of a Directive

        json_body = request["body"]
        if json_body:
            json_object = json.loads(json_body)
            namespace = json_object["directive"]["header"]["namespace"]

            if namespace == "Alexa":
                response = AlexaStateController(json_object["directive"]).process()

            if namespace == "Alexa.Authorization":
                response = AlexaAuthorization(json_object["directive"]).process(
                    client_id, client_secret, redirect_uri
                )

            if namespace == "Alexa.Discovery":
                # Given the Access Token, get the User ID
                adr = do_discovery(json_object["directive"])
                response = adr

            if namespace == "Alexa.PowerController":
                controller = AlexaPowerController(json_object["directive"])
                response = controller.process()

            if namespace == "Alexa.ModeController":
                alexa_error_response = AlexaResponse(name="ErrorResponse")
                alexa_error_response.set_payload(
                    {"type": "INTERNAL_ERROR", "message": "Not Yet Implemented"}
                )
                response = alexa_error_response

            if namespace == "Alexa.RangeController":
                controller = AlexaRangeController(json_object["directive"])
                response = controller.process()

            if namespace == "Alexa.ToggleController":
                controller = AlexaToggleController(json_object["directive"])
                response = controller.process()

            if namespace == "Alexa.Cooking":
                controller = AlexaCookingController(json_object["directive"])
                response = controller.process()

        else:
            alexa_error_response = AlexaResponse(name="ErrorResponse")
            alexa_error_response.set_payload(
                {"type": "INTERNAL_ERROR", "message": "Empty Body"}
            )
            response = alexa_error_response

        if response is None:
            # response set to None indicates an unhandled directive, review the logs
            alexa_error_response = AlexaResponse(name="ErrorResponse")
            alexa_error_response.set_payload(
                {
                    "type": "INTERNAL_ERROR",
                    "message": "Empty Response: No response processed. Unhandled Directive.",
                }
            )
            response = alexa_error_response

        logger.info("api_handler_directive.process.response -----")
        print(json.dumps(response.get()))
        return response.get()


def validate_response(response):
    valid = False
    try:
        with open("alexa_smart_home_message_schema.json", "r") as schema_file:
            json_schema = json.load(schema_file)
            validate(response, json_schema)
        valid = True
    except SchemaError as se:
        logger.info("api_handler_directive.validate_response: Invalid Schema")
        print(se.context)
    except ValidationError as ve:
        logger.info("api_handler_directive.validate_response: Invalid Content")
        print(ve.context)

    return valid


def do_discovery(directive):
    """Implement device discovery"""
    access_token = directive["payload"]["scope"]["token"]

    # Spot the default from the Alexa.Discovery sample. Use as a default for development.
    if access_token == "access-token-from-skill":
        logger.warning(
            "api_handler_directive.process.discovery.user_id: Using development user_id of 0"
        )
        user_id = "0"  # <- Useful for development
    else:
        response_user_id = json.loads(ApiAuth.get_user_id(access_token).decode("utf-8"))
        if "error" in response_user_id:
            logger.error(
                "api_handler_directive.process.discovery.user_id: "
                + response_user_id["error_description"]
            )
        user_id = response_user_id["user_id"]
        logger.info(f"api_handler_directive.process.discovery.user_id: {user_id}")

    adr = AlexaResponse(namespace="Alexa.Discovery", name="Discover.Response")

    # Get the list of endpoints to return for a User ID and add them to the response

    for _id in discovery.list_endpoints(user_id):
        endpoint_details = ApiHandlerEndpoint.EndpointDetails()
        endpoint_details.id = _id
        print(
            "LOG api_handler_directive.process.discovery: Found:",
            endpoint_details.id,
            "for user:",
            user_id,
        )
        result = endpoint_details_table.get_item(
            Key={"EndpointId": endpoint_details.id},
        )
        capabilities_string = result["Item"]["Capabilities"]
        endpoint_details.capabilities = json.loads(capabilities_string)
        endpoint_details.description = result["Item"]["Description"]
        endpoint_details.display_categories = json.loads(
            result["Item"]["DisplayCategories"]
        )
        endpoint_details.friendly_name = result["Item"]["FriendlyName"]
        endpoint_details.manufacturer_name = result["Item"]["ManufacturerName"]

        endpoint_details.sku = result["Item"]["SKU"]
        endpoint_details.user_id = result["Item"]["UserId"]

        adr.add_payload_endpoint(
            friendly_name=endpoint_details.friendly_name,
            endpoint_id=endpoint_details.id,
            capabilities=endpoint_details.capabilities,
            display_categories=endpoint_details.display_categories,
            manufacturer_name=endpoint_details.manufacturer_name,
        )

    return adr
