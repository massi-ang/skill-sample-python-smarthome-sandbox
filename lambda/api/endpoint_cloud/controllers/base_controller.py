# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

import json
import boto3
import os
from alexa.skills.smarthome import AlexaResponse
from endpoint_cloud.api_auth import ApiAuth

dynamodb_aws = boto3.resource("dynamodb")



ENDPOINT_DETAILS_TABLE = os.getenv("ENDPOINT_DETAILS_TABLE", "EndpointDetails")
endpoint_details_table = dynamodb_aws.Table(ENDPOINT_DETAILS_TABLE)


class BaseController:
    def __init__(self, directive):
        self.directive = directive
        self.name = directive["header"]["name"]
        self.correlation_token = directive["header"]["correlationToken"]
        self.instance = directive["header"].get("instance", "")
        self.token = directive["endpoint"]["scope"]["token"]
        self.endpoint_id = directive["endpoint"]["endpointId"]
        self.alexa_response = AlexaResponse(
            token=self.token,
            correlation_token=self.correlation_token,
            endpoint_id=self.endpoint_id,
        )
        self.__endpoint = None
        self.user_id = json.loads(ApiAuth.get_user_id(self.token).decode("utf-8"))
        # Here you can add additional initialization that can be useful for all
        # your controllers implementations: eg mqtt clients, api definitions, etc

        #######

    def get_endpoint(self):
        """Retrieves the endpoint"""
        if self.__endpoint == None:
            result = endpoint_details_table.get_item(
                Key={"EndpointId": self.endpoint_id}
            )
            self.__endpoint = result["Item"]

        return self.__endpoint

    def get_capabilities(self):
        """Retrieves the capabilities"""
        print(self.get_endpoint())
        return json.loads(self.get_endpoint()["Capabilities"])

    def get_sku(self):
        return self.get_endpoint()["SKU"]

    def make_error_response(self, e):
        error_response = AlexaResponse(
            name="ErrorResponse",
            payload={"message":{ "error_description":str(e) } },
            token=self.token,
            correlation_token=self.correlation_token,
            endpoint_id=self.endpoint_id,
        )
        return error_response

    def process(self):
        pass
