from colorfield.fields import ColorField
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=256, unique=True)
    description = models.TextField(blank=True)
    color = ColorField(default='#ffffff', null=True, blank=True)
