from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"