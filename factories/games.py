import factory
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker

from .data import GAME_NAMES
from .extras import RelatedFactoryVariableList, UniqueFaker
from .platforms import PlatformFactory

TZ = timezone.get_current_timezone()
fake = Faker()


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'games.Game'
        django_get_or_create = ('title',)

    title = UniqueFaker('random_element', elements=GAME_NAMES)
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))
    description = factory.Faker('paragraph', nb_sentences=3)
    cover = factory.django.ImageField(color=factory.Faker('color'), upload_to='games/covers/')
    price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    stock = factory.Faker('random_int', min=0, max=100)
    released_at = factory.Faker('date_between', start_date='-5y', end_date='today')
    pegi = factory.Faker('random_element', elements=[3, 7, 12, 16, 18])
    category = factory.SubFactory('factories.categories.CategoryFactory')

    @factory.post_generation
    def platforms(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for platform in extracted:
                self.platforms.add(platform)
        else:
            num_platforms = kwargs.get('size', 0)
            for _ in range(num_platforms):
                platform = PlatformFactory()
                self.platforms.add(platform)

    reviews = RelatedFactoryVariableList(
        'factories.games.ReviewFactory',
        factory_related_name='game',
        size=0,
    )


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'games.Review'

    rating = factory.Faker('random_int', min=1, max=5)
    comment = factory.Faker('sentence', nb_words=10)
    game = factory.SubFactory('factories.games.GameFactory')
    author = factory.SubFactory('factories.auth.UserFactory')

    @factory.post_generation
    def created_at(self, create, extracted, **kwargs):
        if not create:
            return
        value = extracted or fake.date_time_this_year(tzinfo=TZ)
        # Avoid extra save
        self.__class__.objects.filter(pk=self.pk).update(created_at=value)
        self.created_at = value

    @factory.post_generation
    def updated_at(self, create, extracted, **kwargs):
        if not create:
            return
        value = extracted or fake.date_time_between(
            start_date=self.created_at + timezone.timedelta(hours=1), tzinfo=TZ
        )
        # Avoid extra save
        self.__class__.objects.filter(pk=self.pk).update(updated_at=value)
        self.updated_at = value
