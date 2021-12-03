# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

import json


import boto3
import os
from alexa.skills.smarthome import AlexaResponse
from endpoint_cloud.api_auth import ApiAuth

dynamodb_aws = boto3.client('dynamodb')

ENDPOINT_DETAILS_TABLE = os.getenv('ENDPOINT_DETAILS_TABLE', 'EndpointDetails')

class BaseController():
    def __init__(self, directive):
        self.directive = directive
        self.name = directive['header']['name']
        self.correlation_token = directive['header']['correlationToken']
        self.instance = directive['header'].get('instance', '')
        self.token = directive['endpoint']['scope']['token']
        self.endpoint_id = directive['endpoint']['endpointId']
        self.alexa_response = AlexaResponse(token=self.token, correlation_token=self.correlation_token, 
            endpoint_id=self.endpoint_id)

        self.user_id = json.loads(
                ApiAuth.get_user_id(self.token).decode("utf-8")
            )
        # Here you can add additional initialization that can be useful for all 
        # your controllers implementations: eg mqtt clients, api definitions, etc

        #######

    def get_capabilities(self):
        '''Retrieves the capabilities for the endpoint
        '''
        result = dynamodb_aws.get_item(TableName=ENDPOINT_DETAILS_TABLE, Key={'EndpointId': {'S': self.endpoint_id}})
        capabilities_string = self.get_db_value(result['Item']['Capabilities'])
        return json.loads(capabilities_string)

    def make_error_response(self, e):
        return AlexaResponse(name='ErrorResponse', message=e)

    def process(self):
        pass