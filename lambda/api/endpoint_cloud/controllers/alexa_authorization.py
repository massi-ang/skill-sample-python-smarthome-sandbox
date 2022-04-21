# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

import json
import boto3
from datetime import datetime, timedelta
import os
from alexa.skills.smarthome.alexa_response import AlexaResponse
from endpoint_cloud.api_auth import ApiAuth
from .base_controller import BaseController

USERS_TABLE = os.getenv("USERS_TABLE", "Users")

class AlexaAuthorization(BaseController):
    def process(self, client_id, client_secret, redirect_uri) -> AlexaResponse:
        grant_code = self.directive["payload"]["grant"]["code"]
        grantee_token = self.directive["payload"]["grantee"]["token"]

        # Spot the default from the Alexa.Discovery sample.
        # Use as a default for development.
        if grantee_token == "access-token-from-skill":
            user_id = "0"  # <- Useful for development
            response_object = {
                "access_token": "INVALID",
                "refresh_token": "INVALID",
                "token_type": "Bearer",
                "expires_in": 9000,
            }
        else:
            # Get the User ID
            if "error" in self.user_id:
                print(
                    "ERROR api_handler_directive.process.authorization.user_id:",
                    self.user_id["error_description"],
                )
                return self.make_error_response(
                    e={
                        "type": "INTERNAL_ERROR",
                        "message": self.user_id,
                    },
                )

        user_id = self.user_id["user_id"]
        print(
            "LOG api_handler_directive.process.authorization.user_id:",
            user_id,
        )

        # Get the Access and Refresh Tokens
        api_auth = ApiAuth()
        print(
            "grant_code",
            grant_code,
            "client_id",
            client_id,
            "client_secret",
            client_secret,
            "redirect_uri",
            redirect_uri,
        )

        response_token = api_auth.get_access_token(
            grant_code, client_id, client_secret, redirect_uri
        )

        response_token_string = response_token.read().decode("utf-8")

        print(
            "LOG api_handler_directive.process.authorization.response_token_string:",
            response_token_string,
        )
        response_object = json.loads(response_token_string)

        if "error" in response_object:
            return self.make_error_response(response_object)

        # Store the retrieved from the Authorization Server
        access_token = response_object["access_token"]
        refresh_token = response_object["refresh_token"]
        token_type = response_object["token_type"]
        expires_in = response_object["expires_in"]

        # Calculate expiration
        expiration_utc = datetime.utcnow() + timedelta(seconds=(int(expires_in) - 5))

        # Store the User Information - This is useful for inspection during development
        table = boto3.resource("dynamodb").Table(USERS_TABLE)
        result = table.put_item(
            Item={
                "UserId": user_id,
                "GrantCode": grant_code,
                "GranteeToken": grantee_token,
                "AccessToken": access_token,
                "ClientId": client_id,
                "ClientSecret": client_secret,
                "ExpirationUTC": expiration_utc.strftime("%Y-%m-%dT%H:%M:%S.00Z"),
                "RedirectUri": redirect_uri,
                "RefreshToken": refresh_token,
                "TokenType": token_type,
            }
        )

        if result["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(
                "LOG api_handler_directive.process.authorization.Users.put_item:",
                result,
            )
            return AlexaResponse(
                namespace="Alexa.Authorization", name="AcceptGrant.Response"
            )
        else:
            error_message = "Error creating User"
            print("ERR api_handler_directive.process.authorization", error_message)
            return self.make_error_response(error_message)
