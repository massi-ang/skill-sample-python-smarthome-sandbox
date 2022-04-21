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
"""Endpoint handling
"""

import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

from endpoint_cloud.api_handler_event import ApiHandlerEvent
from endpoint_cloud import endpoints
from .api_utils import ApiUtils

logger = logging.getLogger(__name__)


dynamodb_aws = boto3.client("dynamodb")
iot_aws = boto3.client("iot")

samples_thing_group_name = "Samples"
ENDPOINT_DETAILS_TABLE = os.getenv("ENDPOINT_DETAILS_TABLE", "EndpointDetails")

endpoint_details_table = boto3.resource("dynamodb").Table(ENDPOINT_DETAILS_TABLE)


class ApiHandlerEndpoint:
    """Class to handle /endpoint API
    """
    class EndpointDetails:
        """Alexa SmartHome Endpoint model
        """
        def __init__(self):
            self.capabilities = ""
            self.description = "Sample Description"
            self.display_categories = "OTHER"
            self.friendly_name = ApiUtils.get_random_color_string() + " Sample Endpoint"
            self.id = "SAMPLE_ENDPOINT_" + ApiUtils.get_code_string(8)
            self.manufacturer_name = "Sample Manufacturer"
            self.sku = "OT00"
            self.user_id = "0"

        def dump(self):
            """Print the endpoint details to stdout
            """
            print("EndpointDetails -----")
            print("capabilities:", self.capabilities)
            print("description:", self.description)
            print("display_categories:", self.display_categories)
            print("friendly_name:", self.friendly_name)
            print("id:", self.id)
            print("manufacturer_name:", self.manufacturer_name)
            print("sku:", self.sku)
            print("user_id:", self.user_id)

    def create(self, request):
        """Create a new endpoint based on the request
        """

        try:
            endpoint_details = self.EndpointDetails()

            # Map our incoming API body to a thing that will virtually represent a discoverable device for Alexa
            json_object = json.loads(request["body"])
            endpoint = json_object["event"]["endpoint"]
            endpoint_details.user_id = endpoint["userId"]  # Expect a Profile
            endpoint_details.capabilities = endpoint["capabilities"]
            endpoint_details.sku = endpoint["sku"]  # A custom endpoint type, ex: SW01

            if "id" in endpoint:
                endpoint_details.id = endpoint["id"]

            if "friendlyName" in endpoint:
                endpoint_details.friendly_name = endpoint["friendlyName"]

            if "manufacturerName" in endpoint:
                endpoint_details.manufacturer_name = endpoint["manufacturerName"]

            if "description" in endpoint:
                endpoint_details.description = endpoint["description"]

            if "displayCategories" in endpoint:
                endpoint_details.display_categories = endpoint["displayCategories"]

            endpoints.create(endpoint_details=endpoint_details)
            # Validate the Samples group is available, if not, create it

            # Create the thing details in DynamoDb
            response = self.create_endpoint(endpoint_details)
            if not ApiUtils.check_response(response):
                print(
                    "ERR api_handler_endpoint.create.create_thing_details.response",
                    response,
                )

            # Send an Event that updates Alexa
            endpoint = {
                "userId": endpoint_details.user_id,
                "id": endpoint_details.id,
                "friendlyName": endpoint_details.friendly_name,
                "sku": endpoint_details.sku,
                "capabilities": endpoint_details.capabilities,
            }

            # Package into an Endpoint Cloud Event which is sent to Alexa
            event_request = {
                "event": {"type": "AddOrUpdateReport", "endpoint": endpoint}
            }
            event_body = {"body": json.dumps(event_request)}
            event = ApiHandlerEvent().create(event_body)
            logger.info(json.dumps(event, indent=2))
            return response

        except KeyError as key_error:
            return "KeyError: " + str(key_error)

    @staticmethod
    def create_endpoint(endpoint_details):
        logger.info("api_handler_endpoint.create_thing_details -----")
        logger.info(
            f"api_handler_endpoint.create_thing_details.endpoint_details {endpoint_details.dump()}",
        )
        logger.info(
            "api_handler_endpoint.create_thing_details Updating Item in SampleEndpointDetails"
        )
        try:
            response = endpoint_details_table.update_item(
                Key={"EndpointId": endpoint_details.id},
                UpdateExpression="SET \
                        Capabilities = :capabilities, \
                        Description = :description, \
                        DisplayCategories = :display_categories, \
                        FriendlyName = :friendly_name, \
                        ManufacturerName = :manufacturer_name, \
                        SKU = :sku, \
                        UserId = :user_id",
                ExpressionAttributeValues={
                    ":capabilities": str(json.dumps(endpoint_details.capabilities)),
                    ":description": str(endpoint_details.description),
                    ":display_categories": str(
                        json.dumps(endpoint_details.display_categories)
                    ),
                    ":friendly_name": str(endpoint_details.friendly_name),
                    ":manufacturer_name": str(endpoint_details.manufacturer_name),
                    ":sku": str(endpoint_details.sku),
                    ":user_id": str(endpoint_details.user_id),
                },
            )
            logger.info(json.dumps(response))
            return response
        except Exception as e:
            logger.error(e)
            return None

    def delete(self, request):
        """Delete the endpoint(s) 

        If endpoint ids are specified in body delete the specific endpoints
        Can also use * to delete all endpoints
        """
        try:
            response = {}
            logger.debug(request)
            json_object = json.loads(request["body"])
            endpoint_ids = []
            delete_all_sample_endpoints = False
            for endpoint_id in json_object:
                # Special Case for * - If any match, delete all
                if endpoint_id == "*":
                    delete_all_sample_endpoints = True
                    break
                endpoint_ids.append(endpoint_id)

            if delete_all_sample_endpoints is True:
                self.delete_samples()
                response = {"message": "Deleted all sample endpoints"}

            for endpoint_id in endpoint_ids:
                endpoints.delete(endpoint_id)
                response = endpoint_details_table.delete_item(
                    Key={"EndpointId": endpoint_id}
                )
                # TODO Check Response
                # TODO UPDATE ALEXA!
                # Send AddOrUpdateReport to Alexa Event Gateway

            return response

        except KeyError as key_error:
            return "KeyError: " + str(key_error)

    def delete_samples(self):
        result = endpoint_details_table.scan()
        items = result["Items"]
        for item in items:
            endpoint_id = item["EndpointId"]
            # Delete from DynamoDB
            response = endpoint_details_table.delete_item(
                Key={"EndpointId": endpoint_id}
            )
            logger.info(
                "LOG api_handler_endpoint.delete_thing.dynamodb_aws.delete_item.response -----"
            )
            logger.info(response)
            endpoints.delete(endpoint_id)

    # TODO Improve response handling

    def read(self, request):
        """Get a specific endpoint, or all if no endpoint_id is specified in the parameters
        """
        try:
            response = []
            parameters = request.get("queryStringParameters", None)
            if parameters is not None and "endpoint_id" in parameters:
                endpoint_id = request["queryStringParameters"]["endpoint_id"]
                response = endpoint_details_table.get_item(
                    Key={"endpoint_id": endpoint_id}
                )
            else:
                list_response = endpoint_details_table.scan()
                if ApiUtils.check_response(list_response):
                    response = list_response["Items"]

            logger.info("api_handler_endpoint.read -----")
            logger.info(json.dumps(response))
            return response

        except ClientError as client_error:
            return "ClientError: " + str(client_error)

        except KeyError as key_error:
            return "KeyError: " + str(key_error)

    # TODO Work in Progress: Update the Endpoint Details
    @staticmethod
    def update(request):
        raise NotImplementedError()
        # TODO Get the endpoint ID
        # TODO With the endpoint ID, Get the endpoint information from IoT
        # TODO With the endpoint ID, Get the endpoint details from DDB
        #     Get the endpoint as JSON pre-configured
        # TODO Send a command to IoT to update the endpoint
        # TODO Send a command to DDB to update the endpoint
        # TODO UPDATE ALEXA!
        # Send AddOrUpdateReport to Alexa Event Gateway

    # TODO Work in Progress: Update Endpoint States
    @staticmethod
    def update_states(request, states):
        raise NotImplementedError()
        # TODO Get the endpoint ID
        # TODO With the endpoint ID, Get the endpoint information from IoT
        # TODO With the endpoint ID, Get the endpoint details from DDB
        #     Get the endpoint as JSON pre-configured
        # TODO Send a command to IoT to update the endpoint
        # TODO Send a command to DDB to update the endpoint
        # TODO UPDATE ALEXA!
        # Send ChangeReport to Alexa Event Gateway
