#!/bin/bash

# Runs unit tests in app/tests.py with all settings file configurations (see core/settings_*)
settings_modules=(
    'settings_allow'
    'settings_nullify'
    'settings_block'
)
sum_retval=0

for module_name in "${settings_modules[@]}"
do
    echo "===================================================="
    echo "Running tests with settings module: $module_name"
    echo "===================================================="
    env DJANGO_SETTINGS_MODULE="core.$module_name" python manage.py test
    let sum_retval+="$?"
done

evaluate_tests () {
    if [ $1 -eq 0 ]
    then
        echo "All test runs passed"
        return 0
    else
        echo "$1 test runs failed"
        return 1
    fi
}

evaluate_tests $sum_retval
