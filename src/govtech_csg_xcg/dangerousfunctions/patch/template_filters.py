# ------------------------------------------------------------------------
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# This file incorporates work covered by the following copyright:
#
# Copyright (c) 2023 Agency for Science, Technology and Research (A*STAR).
#   All rights reserved.
# Copyright (c) 2023 Government Technology Agency (GovTech).
#   All rights reserved.
# ------------------------------------------------------------------------
import django
from django.core.exceptions import PermissionDenied
from django.template.defaultfilters import safe

from govtech_csg_xcg.dangerousfunctions import logger

from .utils import get_strategy

django.template.defaultfilters.orig_safe_ = safe


def patched_safe(string):
    """report or block the use of safe template filter"""
    strategy = get_strategy("safe")
    if strategy.get("report", True):
        logger.warning("'safe' template filter is not permitted")
    if strategy.get("block", False):
        raise PermissionDenied
    # return the raw string to disable the template filter
    return string
