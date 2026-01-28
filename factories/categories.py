import factory
from django.utils.text import slugify
from faker import Faker

from .data import GAME_CATEGORIES
from .extras import UniqueFaker

fake = Faker()


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'categories.Category'
        django_get_or_create = ('name',)

    name = UniqueFaker('random_element', elements=GAME_CATEGORIES)
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))
    description = factory.LazyFunction(lambda: fake.paragraph().rstrip('.'))
    color = factory.Faker('hex_color')
