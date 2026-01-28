from django.db import models


class Platform(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=256, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(
        upload_to='platforms/logos/', default='platforms/logos/default.png', blank=True, null=True
    )
