# -*- coding: utf-8 -*-

# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file except in
# compliance with the License. A copy of the License is located at
#
#    http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import http.client
from urllib.parse import urlencode
from jose import jwt, jwk
import json
import os


class ApiAuth:

    def post_to_api(self, payload):
        connection = http.client.HTTPSConnection("api.amazon.com")
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache"
        }
        connection.request('POST', '/auth/o2/token',
                           urlencode(payload), headers)
        return connection.getresponse()

    def get_access_token(self, code, client_id, client_secret, redirect_uri):
        '''
        This method refreshes the Alexa token to send envent to the Event Gateway on behalf of the user
        '''
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri
        }
        return self.post_to_api(payload)

    @staticmethod
    def getJwks():
        #TODO: retrieve iss from access token
        connection = http.client.HTTPSConnection(
            "cognito-idp.{}.amazonaws.com".format(os.environ['POOL_ID'].split('_')[0]))
        headers = {
            'content-type': "application/json",
        }
        connection.request('GET', '/{}/.well-known/jwks.json'.format(os.environ['POOL_ID']), headers=headers)
        return json.loads(connection.getresponse().read())

    @staticmethod
    def get_user_id(access_token):
        '''
        This method extract the user id form the the Skill Access Token
        '''
        
        jwks = ApiAuth.getJwks()
        try: 
            decoded_token = jwt.decode(access_token, jwks['keys'])
            return {'user_id': decoded_token['sub']}
        except Exception as ex:
            return { 'error': str(ex) }
        

    def refresh_access_token(self, refresh_token, client_id, client_secret, redirect_uri):
        '''
        This method refreshes the Alexa token to send envent to the Event Gateway on behalf of the user
        '''
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri
        }
        return self.post_to_api(payload)
