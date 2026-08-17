# Dangerous Functions

The Dangerous Functions package contains a [**Django application**](https://docs.djangoproject.com/en/stable/ref/applications/) that nullifies the effects of unsafe Python or Django functions, and logs all invocations of dangerous functions by default. Disabling dangerous functions in Python and Django is an effective way to eradicate Remote Code Execution (RCE), Cross-Site Sripting (XSS) and SQL injection (SQLi) vulnerabilities.

> **Caution:**
> The Dangerous Functions package nullifies a dangerous function by switching it out for a dummy function: this behaviour minimises the impact on applications that may have dependencies that invoke dangerous functions but may still result in regression issues when the dangerous functions do not execute as expected.
>
> The Dangerous Functions package provide a configuration option to raise an exception if dangerous functions are invocated. Refer to [**Usage**](#usage) section for more information.


The following is a list of unsafe Python and Django functions that the Dangerous Functions package nullifies by default:


| Function                              | Description                                                                                                                                                           |
| :------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **safe**                              | Django built-in template filter for marking a string as safe, preventing it from being escaped when rendered.                                                         |
| **os.system**                         | Allows execution of Python strings in a subshell.                                                                                                                     |
| **os.popen**                          | Opens a pipe from a command which allows the command to send its output to another command to be executed.                                                            |
| **subprocess.Popen**                  | Allows execution of Python strings as a subprocess.                                                                                                                   |
| **subprocess.check_output**           | Allows execution of Python strings as a subprocess, and returns the standard output of the command.                                                                   |
| **django.db.models.Manager.raw**      | Django build-in function that allows for raw (unsanitised) queries to Django's models.                                                                                |
| **django.db.connection.cursor**       | Django build-in function that allows for database connection and direct queries to Django's models.                                                                   |
| **builtins.eval**                     | Allows execution of Python string as code.                                                                                                                            |
| **builtins.exec**                     | Allows execution of Python string as code.                                                                                                                            |
| **django.utils.safestring.mark_safe** | Django built-in function for HTML template content that does not check for unsafe HTML elements within code.                                                          |

Dangerous Functions package allow the following configuration options:
- Block and raise an exception when specific dangerous functions are invoked (instead of nullification).
- Disable logging when specific dangerous functions are invoked (instead of logging by default).

## Installation

The Dangerous Functions package can be installed using the command below:

```sh
pip install govtech-csg-xcg-dangerousfunctions
```

Source code for the package can be found at https://github.com/GovTech-CSG/govtech-csg-xcg-dangerousfunctions.

## Setup

Within the `settings.py` Django file (typically located under your project directory):
**File: `./<PROJECT_NAME>/settings.py`**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'your-app',
    'govtech_csg_xcg.dangerousfunctions',
]
```

### Logging

The package uses its own logger with the name `dangerousfunctions`. By default, this logger uses a stream handler and emits messages with level `INFO` and above. The log message format looks something like this:

`2023-06-22 09:50:43,348 [INFO][XCG][dangerousfunctions]: This is an informational message`.

To safely override the default logging configuration, you can write code in `settings.py` to import the logger from the package and modify it directly. The example below sets the logger's level to `DEBUG`:

**File: `settings.py`**
```python
from govtech_csg_xcg.dangerousfunctions import logger
import logging

logger.setLevel(logging.DEBUG)
```

For more information on the Python logging library, see the [**official documentation**](https://docs.python.org/3/library/logging.html).

## Usage

By default, Dangerous Functions package nullifies and logs all invocations of dangerous functions.

### Block & Log Dangerous Functions

To raise a 403 exception (`block`) and log (`report`) the execution of dangerous function, configure `settings.py` as follows:
**File: `./<PROJECT_NAME>/settings.py`**
```python
XCG_DANGEROUS_FUNCTIONS
  'os.system':{
    'block': True, # Raises 403 error to user
    'report': True, # Logs execution of function
  },
  ...
}
```

When `os.system` is invoked with the above configuration, Django will:

1. Output the following log:
```
'os.system' is not permitted
```
2. Raise a `django.core.exceptions.PermissionDenied` exception, which will cause Django to return either:
    1. Your custom 403 page, if you provided a template named 403.html in your root template directory, or
    2. Plain text saying "403 Forbidden" otherwise.


## Configuration Options

- `block` Setting:
  - Default: `False`. If set to `True`, whenever the dangerous function is run, it is blocked and the user is
  returned a 403 HTTP response.
- `report` Setting:
  - Default: `True`. If set to `True`, whenever the dangerous function is run, the invocation attempt is logged and the function's effects are silently nullified.
- Function names:
  - `os.system`
  - `os.popen`
  - `subprocess.popen`
  - `subprocess.check_output`
  - `Manager.raw`
  - `connection.cursor`
  - `eval`
  - `exec`
  - `mark_safe`
  - `safe`

> **Caution:**
> This module aims to nullify the dangerous behaviours introduced only by user-defined code within the Django project. This is achieved by checking the call stack to verify if the code lives within the project.
>
> Since Django processes templates using various template engines, the `safe` template filter is invoked by Django's library code, not directly by code within the user's project. Therefore, `dangerousfunctions` cannot differentiate between the use of the `safe` template filter in user-defined templates and in third-party library templates. As a result, this module can accidentally remove the functionality of `safe` template filters in third-party libraries, potentially breaking their functionality. Generally this should be rare, and should not cause any critical issues, but please do let us know if it affects your application.

