import factory
from django.utils import timezone
from faker import Faker

from .extras import UniqueFaker

fake = Faker()
TZ = timezone.get_current_timezone()


class TokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.Token'

    key = UniqueFaker('uuid4')

    @factory.post_generation
    def created_at(self, create, extracted, **kwargs):
        if not create:
            return
        value = extracted or fake.date_time_this_year(tzinfo=TZ)
        # Avoid extra save
        self.__class__.objects.filter(pk=self.pk).update(created_at=value)
        self.created_at = value
