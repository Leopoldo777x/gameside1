import factory
from django.utils import timezone
from faker import Faker

from .games import GameFactory

TZ = timezone.get_current_timezone()
fake = Faker()


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'orders.Order'

    status = factory.Faker('random_element', elements=[1, 2, 3, -1])
    key = factory.Faker('uuid4')
    user = factory.SubFactory('factories.auth.UserFactory')

    @factory.post_generation
    def games(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for game in extracted:
                self.games.add(game)
        else:
            num_games = kwargs.get('size', 0)
            for _ in range(num_games):
                game = GameFactory()
                self.games.add(game)

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
