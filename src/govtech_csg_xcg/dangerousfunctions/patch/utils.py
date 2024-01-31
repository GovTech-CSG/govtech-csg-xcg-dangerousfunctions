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
import inspect
import pprint

from django.conf import settings
from django.core.handlers.base import BaseHandler

from . import _thread_flags


def get_strategy(sig):
    """get the strategy for the specified function"""
    if not hasattr(settings, "XCG_DANGEROUS_FUNCTIONS"):
        middleware_settings = {}
    else:
        middleware_settings = settings.XCG_DANGEROUS_FUNCTIONS
    return middleware_settings.get(sig, {})


def debug():
    """print stack information"""
    stack_info = inspect.stack()
    for stack in stack_info:
        pprint.pprint(stack)


def get_info_from_stack(depth=2):
    """get source code information from `inspect.stack()`"""
    stack_info = inspect.stack()
    target_frame = stack_info[depth]
    return (
        target_frame.filename,
        target_frame.lineno,
        target_frame.function,
        target_frame.code_context,
    )


def in_scope(filename: str) -> bool:
    """determine whether the file is inside the django project"""
    # TODO: improve this function
    if filename is None:
        return False
    return filename.startswith(str(settings.BASE_DIR))


BaseHandler.load_middleware_orig_ = BaseHandler.load_middleware


def load_middleware_flag(self):
    """Patch `BaseHandler.load_middleware` to disable `exec()`
    patching during loading middleware"""
    _thread_flags.loading_middleware = True
    BaseHandler.load_middleware_orig_(self)
    _thread_flags.loading_middleware = False
