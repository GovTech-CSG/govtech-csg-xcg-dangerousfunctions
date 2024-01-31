from django import forms


class CmdForm(forms.Form):
    cmd = forms.CharField(label="Command you want to execute:", max_length=100)


class SQLForm(forms.Form):
    sql_query = forms.CharField(
        label="SQL query you want to execute against the app_testmodel table:",
        max_length=100,
    )


class ReflectForm(forms.Form):
    html = forms.CharField(label="Enter some HTML:", max_length=200)
