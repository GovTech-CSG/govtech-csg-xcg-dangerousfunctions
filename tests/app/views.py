import os
import subprocess
from collections import namedtuple
from os import system

from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import safestring

from .forms import CmdForm, ReflectForm, SQLForm
from .models import TestModel


def execute_dangerous_function(
    request, form_class, dangerous_function, template_name, view_name
):
    results = None
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            payload = None
            if issubclass(form_class, CmdForm):
                payload = form.cleaned_data["cmd"]
            elif issubclass(form_class, SQLForm):
                payload = form.cleaned_data["sql_query"]
            elif issubclass(form_class, ReflectForm):
                payload = form.cleaned_data["html"]
            results = dangerous_function(payload)
    else:
        form = form_class()

    return render(
        request,
        template_name,
        {"url": reverse_lazy(view_name), "form": form, "results": results},
    )


def os_system(request):
    return execute_dangerous_function(
        request, CmdForm, os.system, "post_form.html", "os-system"
    )


def os_system_from_import(request):
    return execute_dangerous_function(
        request, CmdForm, system, "post_form.html", "os-system-from-import"
    )


def os_popen(request):
    def execute_os_popen(cmd):
        with os.popen(cmd) as pipe:
            return pipe.read()

    return execute_dangerous_function(
        request, CmdForm, execute_os_popen, "post_form.html", "os-popen"
    )


def subprocess_popen(request):
    def execute_subprocess_popen(cmd):
        popen_obj = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return popen_obj.stdout.read().decode("utf-8")

    return execute_dangerous_function(
        request, CmdForm, execute_subprocess_popen, "post_form.html", "subprocess-popen"
    )


def subprocess_check_output(request):
    def execute_subprocess_check_output(cmd):
        try:
            return subprocess.check_output(cmd, shell=True).decode("utf-8")
        except Exception as e:
            if isinstance(e, PermissionDenied):
                raise e
            return str(e)

    return execute_dangerous_function(
        request,
        CmdForm,
        execute_subprocess_check_output,
        "post_form.html",
        "subprocess-check-output",
    )


def manager_raw(request):
    # Example SQL statement: SELECT * FROM app_testmodel
    def execute_manager_raw(sql):
        objects = TestModel.objects.raw(sql)
        if objects:
            return [instance.name for instance in objects]
        else:
            return "No results from SQL"

    return execute_dangerous_function(
        request, SQLForm, execute_manager_raw, "post_form.html", "manager-raw"
    )


def connection_cursor(request):
    # Example SQL statement: SELECT * FROM app_testmodel
    def execute_connection_cursor(sql):
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        if rows:
            return rows
        else:
            return "No results from SQL"

    return execute_dangerous_function(
        request,
        SQLForm,
        execute_connection_cursor,
        "post_form.html",
        "connection-cursor",
    )


def eval_view(request):
    # Note: `eval` can only evaluate EXPRESSIONS, which means multiline programs
    # can't be run. Working example: `os.getenv('DJANGO_SETTINGS_MODULE').split('_')`
    return execute_dangerous_function(request, CmdForm, eval, "post_form.html", "eval")


def exec_view(request):
    return execute_dangerous_function(request, CmdForm, exec, "post_form.html", "exec")


def mark_safe_view(request):
    return execute_dangerous_function(
        request, ReflectForm, safestring.mark_safe, "post_form.html", "mark-safe"
    )


def safe_template_filter(request):
    return execute_dangerous_function(
        request,
        ReflectForm,
        lambda html: html,
        "post_form_safe.html",
        "safe-template-filter",
    )


def named_tuple(request):
    # namedtuple uses eval(), this is to test whether third-party libraries
    # can use eval() without issue
    Point = namedtuple("Point", "x y")
    point = Point(2, 4)
    return HttpResponse(point)
