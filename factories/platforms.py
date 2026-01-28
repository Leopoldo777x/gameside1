import factory
from django.utils.text import slugify

from .data import GAME_PLATFORMS
from .extras import UniqueFaker


class PlatformFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'platforms.Platform'
        django_get_or_create = ('name',)

    name = UniqueFaker('random_element', elements=GAME_PLATFORMS)
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))
    description = factory.Faker('paragraph', nb_sentences=2)
    logo = factory.django.ImageField(color=factory.Faker('color'), upload_to='platforms/logos/')
