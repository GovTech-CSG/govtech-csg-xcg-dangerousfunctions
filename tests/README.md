# Tests for `govtech-csg-xcg-dangerousfunctions`

This directory contains a dummy Django application used for testing the `govtech-csg-xcg-dangerousfunctions` package. For details on how to execute tests, see details below.

Before running any tests, remember to apply all database migrations by running the command: `python3 manage.py migrate`

## Specifying the settings module

The [`manage.py`](./manage.py) script has been modified to set `core.settings_nullify` as the default value for the `DJANGO_SETTINGS_MODULE` environment variable. To override this, run the command below:

```sh
export DJANGO_SETTINGS_MODULE='<core.settings_allow | core.settings_block | core.your_own_settings_module>'
```

The three available settings modules are:

1. `core.settings_allow` - Disables the `dangerousfunctions` package so that dangerous functions can be invoked. This acts as a control.
2. `core.settings_nullify` - Enables the `dangerousfunctions` package with default configuration, which causes dangerous functions to be "nullified" (i.e. silently stopped).
3. `core.settings_block` - Enables the `dangerousfunctions` package and configures it to "block" dangerous functions (i.e. raise exception and return 403 forbidden response).

## Running unit tests

As the different test cases correspond to the different settings configurations, a helper script has been provided to run the test suite using each of the settings modules in turn. Run all tests using the command below:

```sh
/bin/bash run_all_tests.sh
```

## Manual testing

Run the local development server using the following command:

```sh
python3 manage.py runserver
```

Then visit `http://localhost:8000/app/<function_to_test>` in your web browser. Refer to [the URLConf file](./app/urls.py) for a mapping of URLs to view functions testing specific dangerous functions. For example, to test the `subprocess.check_output` function, visit `http://localhost:8000/app/subprocess_check_output`.
