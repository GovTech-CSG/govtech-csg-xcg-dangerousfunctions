from django.urls import path

from . import views

urlpatterns = [
    path("os_system/", views.os_system, name="os-system"),
    path(
        "os_system_from_import/",
        views.os_system_from_import,
        name="os-system-from-import",
    ),
    path("os_popen/", views.os_popen, name="os-popen"),
    path("subprocess_popen/", views.subprocess_popen, name="subprocess-popen"),
    path(
        "subprocess_check_output/",
        views.subprocess_check_output,
        name="subprocess-check-output",
    ),
    path("manager_raw/", views.manager_raw, name="manager-raw"),
    path("connection_cursor/", views.connection_cursor, name="connection-cursor"),
    path("eval/", views.eval_view, name="eval"),
    path("exec/", views.exec_view, name="exec"),
    path("mark_safe/", views.mark_safe_view, name="mark-safe"),
    path(
        "safe_template_filter/", views.safe_template_filter, name="safe-template-filter"
    ),
    path("named_tuple/", views.named_tuple, name="named-tuple"),
]
