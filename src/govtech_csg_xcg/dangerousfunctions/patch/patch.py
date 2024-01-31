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
import builtins
import os
import subprocess

import django
from django.core.handlers.base import BaseHandler
from django.db.backends.base.base import BaseDatabaseWrapper

from . import functions, utils
from .template_filters import patched_safe


class Patcher:
    """this class will do the patching and reverting of dangerous functions"""

    @classmethod
    def do_patch(cls):
        """this function will monkey patch dangerous functions"""
        django.template.defaultfilters.register.filter("safe", patched_safe)
        os.system = functions.patched_os_system
        os.popen = functions.patched_os_popen
        subprocess.Popen = functions.patched_subprocess_popen
        subprocess.check_output = functions.patched_check_output
        django.db.models.Manager.raw = functions.patched_manager_raw
        BaseDatabaseWrapper.cursor = functions.patched_connection_cursor
        builtins.eval = functions.patched_eval
        builtins.exec = functions.patched_exec
        django.utils.safestring.mark_safe = functions.patched_mark_safe
        BaseHandler.load_middleware = utils.load_middleware_flag

    @classmethod
    def revert(cls):
        """this function will revert back the original functions"""
        django.template.defaultfilters.register.filter(
            "safe", django.template.defaultfilters.orig_safe_
        )
        os.system = os.orig_system_
        os.popen = os.orig_popen_
        subprocess.Popen = subprocess.orig_Popen_
        subprocess.check_output = subprocess.orig_check_output_
        django.db.models.Manager.raw = django.db.models.Manager.orig_raw_
        BaseDatabaseWrapper.cursor = BaseDatabaseWrapper.orig_cursor_
        builtins.eval = builtins.orig_eval_
        builtins.exec = builtins.orig_exec_
        django.utils.safestring.mark_safe = django.utils.safestring.orig_mark_safe_
