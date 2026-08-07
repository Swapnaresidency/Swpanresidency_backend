from django.db import models
from django.contrib.auth.models import AbstractUser


class Institution(models.Model):
    name = models.CharField(max_length=200)

    code = models.CharField(
        max_length=20,
        unique=True
    )

    address = models.TextField()

    logo = models.ImageField(
        upload_to="institution/logo/",
        blank=True,
        null=True
    )

    mobile = models.CharField(max_length=15)

    email = models.EmailField()

    gstin = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    active = models.BooleanField(default=True)

    class Meta:
        db_table = "admn_instn_master"
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    mobile = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    class Meta:
        db_table = "admn_user"

    def __str__(self):
        return self.username