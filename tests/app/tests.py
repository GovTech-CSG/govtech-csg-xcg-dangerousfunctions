import logging
import os
from unittest import skipUnless

from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape
from parameterized import parameterized

# Turn off logging for the duration of tests
logger = logging.getLogger("dangerousfunctions")
logger.setLevel(logging.ERROR)


def cleanup():
    try:
        os.remove("test_file")
    except FileNotFoundError:
        pass


@skipUnless(
    os.environ["DJANGO_SETTINGS_MODULE"] == "core.settings_allow",
    "Requires core.settings_allow",
)
class TestDangerousFunctionsRunWithoutPackage(TestCase):
    """Test case for the scenario where the dangerousfunctions package is not in use.

    In such a scenario, each dangerous function should be allowed to execute.
    This test case serves as a control for the subsequent test cases where
    the package is activated.
    """

    @classmethod
    def setUpClass(cls):
        # Ensure that no test file exists at the start of this test case.
        cleanup()
        super().setUpClass()

    def tearDown(self):
        # Ensure test file is removed between test method runs.
        cleanup()

    @parameterized.expand(
        [
            "os-system",
            "os-popen",
            "subprocess-popen",
            "subprocess-check-output",
        ]
    )
    def test_os_command_functions_work_without_dangerousfunctions(self, view_name):
        response = self.client.post(
            reverse(view_name), {"cmd": "echo test_os > test_file"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.exists("test_file"))
        with open("test_file") as f:
            content = f.read()
            self.assertEqual(content.strip(), "test_os")

    @parameterized.expand(
        [
            "eval",
            "exec",
        ]
    )
    def test_python_command_functions_work_without_dangerousfunctions(self, view_name):
        response = self.client.post(
            reverse(view_name),
            {"cmd": 'open("test_file", "w").write("test_exec_eval")'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.exists("test_file"))
        with open("test_file") as f:
            content = f.read()
            self.assertEqual(content.strip(), "test_exec_eval")

    @parameterized.expand(
        [
            "manager-raw",
            "connection-cursor",
        ]
    )
    def test_raw_sql_works_without_dangerousfunctions(self, view_name):
        response = self.client.post(
            reverse(view_name), {"sql_query": "SELECT * FROM app_testmodel WHERE id=1"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test_instance_1")

    @parameterized.expand(["mark-safe", "safe-template-filter"])
    def test_unsafe_html_works_without_dangerousfunctions(self, view_name):
        script = "<script>alert(1)</script>"
        response = self.client.post(reverse(view_name), {"html": script})

        self.assertEqual(response.status_code, 200)
        # As long as the script string is shown unescaped
        # it means the XSS attack will succeed
        self.assertContains(response, script)


@skipUnless(
    os.environ["DJANGO_SETTINGS_MODULE"] == "core.settings_nullify",
    "Requires core.settings_nullify",
)
class TestDangerousFunctionsNullifiedByPackage(TestCase):
    """Test case for the scenario where the dangerousfunctions package
    is in use in its default configuration.

    In such a scenario, dangerous functions should be "nullified",
    i.e. a dummy version is executed and therefore intended behaviours
    should not be observed.
    """

    @parameterized.expand(
        [
            "os-system",
            "os-popen",
            "subprocess-popen",
            "subprocess-check-output",
        ]
    )
    def test_os_command_functions_nullified(self, view_name):
        response = self.client.post(
            reverse(view_name), {"cmd": "echo test_os > test_file"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(os.path.exists("test_file"))

    @parameterized.expand(
        [
            "eval",
            "exec",
        ]
    )
    def test_python_command_functions_nullified(self, view_name):
        response = self.client.post(
            reverse(view_name),
            {"cmd": 'open("test_file", "w").write("test_exec_eval")'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(os.path.exists("test_file"))

    @parameterized.expand(
        [
            "manager-raw",
            "connection-cursor",
        ]
    )
    def test_raw_sql_nullified(self, view_name):
        response = self.client.post(
            reverse(view_name), {"sql_query": "SELECT * FROM app_testmodel WHERE id=1"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No results from SQL")

    @parameterized.expand(["mark-safe", "safe-template-filter"])
    def test_unsafe_html_nullified(self, view_name):
        script = "<script>alert(1)</script>"
        response = self.client.post(reverse(view_name), {"html": script})

        self.assertEqual(response.status_code, 200)
        # We check for the escaped version here
        self.assertContains(response, escape(script))


@skipUnless(
    os.environ["DJANGO_SETTINGS_MODULE"] == "core.settings_block",
    "Requires core.settings_block",
)
class TestDangerousFunctionsBlockedByPackage(TestCase):
    """Test case for the scenario where the dangerousfunctions package
    is in use and is configured to block invocations.

    In such a scenario, dangerous functions should be "blocked", which means a dummy
    version is executed that raises a django.core.exceptions.PermissionDenied exception,
    which should result in the application returning a 403 Forbidden HTTP response.
    """

    @parameterized.expand(
        [
            "os-system",
            "os-popen",
            "subprocess-popen",
            "subprocess-check-output",
        ]
    )
    def test_os_command_functions_blocked(self, view_name):
        response = self.client.post(
            reverse(view_name), {"cmd": "echo test_os > test_file"}
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(os.path.exists("test_file"))

    @parameterized.expand(
        [
            "eval",
            "exec",
        ]
    )
    def test_python_command_functions_blocked(self, view_name):
        response = self.client.post(
            reverse(view_name),
            {"cmd": 'open("test_file", "w").write("test_exec_eval")'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(os.path.exists("test_file"))

    @parameterized.expand(
        [
            "manager-raw",
            "connection-cursor",
        ]
    )
    def test_raw_sql_blocked(self, view_name):
        response = self.client.post(
            reverse(view_name), {"sql_query": "SELECT * FROM app_testmodel WHERE id=1"}
        )

        self.assertEqual(response.status_code, 403)

    @parameterized.expand(["mark-safe", "safe-template-filter"])
    def test_unsafe_html_blocked(self, view_name):
        script = "<script>alert(1)</script>"
        response = self.client.post(reverse(view_name), {"html": script})

        self.assertEqual(response.status_code, 403)
