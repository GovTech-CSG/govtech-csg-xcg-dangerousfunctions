from django.db import models


# Create your models here.
class TestModel(models.Model):
    """Test model for testing raw SQL queries."""

    name = models.CharField(max_length=50)
