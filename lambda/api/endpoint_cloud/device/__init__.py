# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

'''Implementation of a device using AWS IoT
'''

import boto3
import os

iot_data_aws = boto3.client('iot-data', endpoint_url=os.getenv('IOT_ENDPOINT_URL'))
iot_aws = boto3.client('iot')

