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
from unittest.mock import MagicMock

import django
from django.core.exceptions import PermissionDenied
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models.query import RawQuerySet

from govtech_csg_xcg.dangerousfunctions import logger

from . import _thread_flags
from .utils import get_info_from_stack, get_strategy, in_scope

os.orig_system_ = os.system


def patched_os_system(*args, **kwargs) -> int:
    """log or disable the use of os.system"""

    # although it is rare, but it is possible that the function is called
    # during the loading of middleware. In this case, we should not
    # block the function.
    if getattr(_thread_flags, "loading_middleware", False):
        return os.orig_system_(*args, **kwargs)

    filename, line, func, code = get_info_from_stack()

    # if cannot get the source code, it is very likely that the function
    # is not called by user code.
    if code is None:
        return os.orig_system_(*args, **kwargs)

    # check whether the function is called by libraries
    if not in_scope(filename):
        return os.orig_system_(*args, **kwargs)

    strategy = get_strategy("os.system")
    if strategy.get("report", True):
        logger.warning("'os.system' is not permitted")
        logger.warning(f"in file {filename} line {line} function {func}")
        logger.warning(f"source code: {code}")

    if strategy.get("block", False):
        raise PermissionDenied

    # 0 indicates that the command is executed successfully
    return 0


os.orig_popen_ = os.popen


def patched_os_popen(*args, **kwargs):
    """log or disable the use of os.popen"""

    # conduct quick check to improve performance
    if getattr(_thread_flags, "loading_middleware", False):
        return os.orig_popen_(*args, **kwargs)

    filename, line, func, code = get_info_from_stack()

    # if cannot get the source code, it is very likely that the function
    # is not called by user code.
    if code is None:
        return os.orig_popen_(*args, **kwargs)

    # check whether the function is called by libraries
    if not in_scope(filename):
        return os.orig_popen_(*args, **kwargs)

    strategy = get_strategy("os.popen")
    if strategy.get("report", True):
        logger.warning("'os.popen' is not permitted")
        logger.warning(f"in file {filename} line {line} function {func}")
        logger.warning(f"source code: {code}")

    if strategy.get("block", False):
        raise PermissionDenied

    # `:` does nothing in a shell, feed it to the original popen to disarm it
    # without break any following functions.
    return os.orig_popen_(":")


subprocess.orig_Popen_ = subprocess.Popen


def patched_subprocess_popen(*args, **kwargs):
    """report or block use of subprocess.Popen"""

    # conduct quick check to improve performance
    if getattr(_thread_flags, "loading_middleware", False):
        return subprocess.orig_Popen_(*args, **kwargs)
    filename, line, func, code = get_info_from_stack()

    # if cannot get the source code, it is very likely that the function
    # is not called by user code.
    if code is None:
        return subprocess.orig_Popen_(*args, **kwargs)

    # check whether the function is called by libraries
    if not in_scope(filename):
        return subprocess.orig_Popen_(*args, **kwargs)

    strategy = get_strategy("subprocess.popen")
    if strategy.get("report", True):
        logger.warning("'subprocess.popen' is not permitted")
        logger.warning(f"in file {filename} line {line} function {func}")
        logger.warning(f"source code: {code}")

    if strategy.get("block", False):
        raise PermissionDenied

    # `:` does nothing in a shell, feed it to the original Popen to disarm it
    # without break any following functions.
    kwargs["shell"] = True
    return subprocess.orig_Popen_(":", **kwargs)


subprocess.orig_check_output_ = subprocess.check_output


def patched_check_output(*args, **kwargs):
    """report or block use of subprocess.check_output"""

    # conduct quick check to improve performance
    if getattr(_thread_flags, "loading_middleware", False):
        return subprocess.orig_check_output_(*args, **kwargs)
    filename, line, func, code = get_info_from_stack()

    # if cannot get the source code, it is very likely that the function
    # is not called by user code.
    if code is None:
        return subprocess.orig_check_output_(*args, **kwargs)

    # check whether the function is called by libraries
    if not in_scope(filename):
        return subprocess.orig_check_output_(*args, **kwargs)

    strategy = get_strategy("subprocess.check_output")
    if strategy.get("report", True):
        logger.warning("'subprocess.check_output' is not permitted")
        logger.warning(f"in file {filename} line {line} function {func}")
        logger.warning(f"source code: {code}")

    if strategy.get("block", False):
        raise PermissionDenied

    return b""


django.db.models.Manager.orig_raw_ = django.db.models.Manager.raw


def patched_manager_raw(*args, **kwargs) -> RawQuerySet:
    """report or block use of Manager.raw"""

    # conduct quick check to improve performance
    if getattr(_thread_flags, "loading_middleware", False):
        return django.db.models.Manager.orig_raw_(*args, **kwargs)

    filename, line, func, code = get_info_from_stack()

    # if cannot get the source code, it is very likely that the function
    # is not called by user code.
    if code is None:
        return django.db.models.Manager.orig_raw_(*args, **kwargs)

    # check whether the function is called by libraries
    if not in_scope(filename):
        return django.db.models.Manager.orig_raw_(*args, **kwargs)

    strategy = get_strategy("Manager.raw")
    if strategy.get("report", True):
        logger.warning("'Manager.raw' is not permitted")
        logger.warning(f"in file {filename} line {line} function {func}")
        logger.warning(f"source code: {code}")

    if strategy.get("block", False):
        raise PermissionDenied

    # Manager.raw() will return None if no record found in db
    return


BaseDatabaseWrapper.orig_cursor_ = BaseDatabaseWrapper.cursor


def patched_connection_cursor(*args, **kwargs):
    """report or block use of connection.cursor"""

    # conduct quick check to improve performance
    if getattr(_thread_flags, "loading_middleware", False):
        return django.db.backends.base.base.BaseDatabaseWrapper.orig_cursor_(
            *args, **kwargs
        )

    filename, line, func, code = get_info_from_stack()

    if not in_scope(filename):
        return django.db.backends.base.base.BaseDatabaseWrapper.orig_cursor_(
            *args, **kwargs
        )

    strategy = get_strategy("connection.cursor")
    if strategy.get("report", True):
        logger.warning("'connection.cursor' is not permitted")
        logger.warning(f"in file {filename} line {line} function {func}")
        logger.warning(f"source code: {code}")

    if strategy.get("block", False):
        raise PermissionDenied

    # handles with...as condition
    enter = MagicMock()
    enter.fetchone.return_value = None
    enter.fetchall.return_value = []
    mock = MagicMock()
    mock.__enter__.return_value = enter
    # handles direct call cursor()
    mock.fetchone.return_value = None
    mock.fetchall.return_value = []
    return mock


builtins.orig_eval_ = builtins.eval


def patched_eval(*args, **kwargs):
    """report or block use of eval"""

    # conduct quick check to improve performance
    if getattr(_thread_flags, "loading_middleware", False):
        return builtins.orig_eval_(*args, **kwargs)

    filename, line, func, code = get_info_from_stack()

    # if cannot get the source code, it is very likely that the function
    # is not called by user code.
    if code is None:
        return builtins.orig_eval_(*args, **kwargs)

    # check whether the function is called by libraries
    if not in_scope(filename):
        return builtins.orig_eval_(*args, **kwargs)

    strategy = get_strategy("eval")
    if strategy.get("report", True):
        logger.warning("'eval' is not permitted")
        logger.warning(f"in file {filename} line {line} function {func}")
        logger.warning(f"source code: {code}")

    if strategy.get("block", False):
        raise PermissionDenied

    return


builtins.orig_exec_ = builtins.exec


def patched_exec(*args, **kwargs):
    """report or block use of exec"""
    # disable exec patching during middleware initialization to improve performance
    # set the default value to True to disable the patching during initialization of
    # other components as well
    if getattr(_thread_flags, "loading_middleware", False):
        return builtins.orig_exec_(*args, **kwargs)

    filename, line, func, code = get_info_from_stack()
    # If we cannot get the source code, it is very likely
    # that the exec is not from user code.
    if code is None:
        return builtins.orig_exec_(*args, **kwargs)

    # check whether the function is called by libraries
    if not in_scope(filename):
        return builtins.orig_exec_(*args, **kwargs)

    strategy = get_strategy("exec")
    if strategy.get("report", True):
        logger.warning("'exec' is not permitted")
        logger.warning(f"in file {filename} line {line} function {func}")
        logger.warning(f"source code: {code}")

    if strategy.get("block", False):
        raise PermissionDenied

    return


django.utils.safestring.orig_mark_safe_ = django.utils.safestring.mark_safe


def patched_mark_safe(s):
    """report or block use of mark_safe"""

    # although it is rare, conduct quick check to improve performance
    if getattr(_thread_flags, "loading_middleware", False):
        return django.utils.safestring.orig_mark_safe_(s)

    filename, line, func, code = get_info_from_stack()

    if not in_scope(filename):
        return django.utils.safestring.orig_mark_safe_(s)

    strategy = get_strategy("mark_safe")
    if strategy.get("report", True):
        logger.warning("'mark_safe' is not permitted")
        logger.warning(f"in file {filename} line {line} function {func}")
        logger.warning(f"source code: {code}")

    if strategy.get("block", False):
        raise PermissionDenied

    return s
