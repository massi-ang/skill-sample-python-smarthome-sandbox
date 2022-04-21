# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT
"""Module
"""

import os

from .alexa_toggle_controller import AlexaToggleController
from .alexa_range_controller import AlexaRangeController
from .alexa_power_controller import AlexaPowerController
from .alexa_cooking_controller import AlexaCookingController
from .alexa_authorization import AlexaAuthorization
from .alexa_state_controller import AlexaStateController

ENDPOINT_DETAILS_TABLE = os.getenv("ENDPOINT_DETAILS_TABLE")
