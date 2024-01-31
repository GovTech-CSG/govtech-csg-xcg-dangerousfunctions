from django.db import migrations


def create_test_instances(apps, schema_editor):
    """Create some test instances for testing raw SQL queries."""
    TestModel = apps.get_model("app", "TestModel")
    for i in range(10):
        TestModel(name=f"test_instance_{str(i + 1)}").save()


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [migrations.RunPython(create_test_instances)]
