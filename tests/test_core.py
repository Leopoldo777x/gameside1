import uuid

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model

from categories.models import Category
from games.models import Game, Review
from orders.models import Order
from platforms.models import Platform
from users.models import Token

User = get_user_model()

# ==============================================================================
# Required Apps
# ==============================================================================


@pytest.mark.django_db
def test_required_apps_are_installed():
    REQUIRED_APPS = ('shared', 'games', 'platforms', 'categories', 'orders', 'users')

    custom_apps = [app for app in settings.INSTALLED_APPS if not app.startswith('django')]
    for app in REQUIRED_APPS:
        app_config = f'{app}.apps.{app.title()}Config'
        assert app_config in custom_apps, (
            f'La aplicación <{app}> no está "creada/instalada" en el proyecto.'
        )
    assert len(custom_apps) >= len(REQUIRED_APPS), (
        'El número de aplicaciones propias definidas en el proyecto no es correcto.'
    )


# ==============================================================================
# Game Model
# ==============================================================================


@pytest.mark.score(2)
@pytest.mark.django_db
def test_game_model_is_correctly_configured():
    # title
    assert (f := Game._meta.get_field('title')), 'Game.title no se ha definido'
    assert f.get_internal_type() == 'CharField', 'Game.title no tiene el tipo esperado'
    assert f.unique, 'Game.title no se ha definido como único'
    assert not f.blank, 'Game.title no debe admitir valores en blanco'

    # slug
    assert (f := Game._meta.get_field('slug')), 'Game.slug no se ha definido'
    assert f.get_internal_type() == 'SlugField', 'Game.slug no tiene el tipo esperado'
    assert f.unique, 'Game.slug no se ha definido como único'
    assert not f.blank, 'Game.slug no debe admitir valores en blanco'

    # description
    assert (f := Game._meta.get_field('description')), 'Game.description no se ha definido'
    assert f.get_internal_type() == 'TextField', 'Game.description no tiene el tipo esperado'
    assert f.blank, 'Game.description no admite valores en blanco'

    # cover
    assert (f := Game._meta.get_field('cover')), 'Game.cover no se ha definido'
    assert f.get_internal_type() in ['FileField', 'ImageField'], (
        'Game.cover no tiene el tipo esperado'
    )
    assert f.upload_to == 'games/covers/', 'Game.cover no tiene la ruta de subida esperada'
    assert f.blank, 'Game.cover no admite valores en blanco'
    assert f.default == 'games/covers/default.png', (
        'Game.cover no tiene el valor por defecto esperado'
    )

    # price
    assert (f := Game._meta.get_field('price')), 'Game.price no se ha definido'
    assert f.get_internal_type() == 'DecimalField', 'Game.price no tiene el tipo esperado'
    assert f.max_digits == 6, 'Game.price no tiene el valor esperado de max_digits'
    assert f.decimal_places == 2, 'Game.price no tiene el valor esperado de decimal_places'
    assert not f.blank, 'Game.price no debe admitir valores en blanco'

    # stock
    assert (f := Game._meta.get_field('stock')), 'Game.stock no se ha definido'
    assert f.get_internal_type() == 'PositiveIntegerField', 'Game.stock no tiene el tipo esperado'
    assert not f.blank, 'Game.stock no debe admitir valores en blanco'

    # released_at
    assert (f := Game._meta.get_field('released_at')), 'Game.released_at no se ha definido'
    assert f.get_internal_type() == 'DateField', 'Game.released_at no tiene el tipo esperado'
    assert not f.auto_now and not f.auto_now_add, (
        'Game.released_at no debe tener auto_now ni auto_now_add activados'
    )
    assert not f.blank, 'Game.released_at no debe admitir valores en blanco'

    # pegi
    assert (f := Game._meta.get_field('pegi')), 'Game.pegi no se ha definido'
    assert f.get_internal_type() == 'PositiveSmallIntegerField', (
        'Game.pegi no tiene el tipo esperado'
    )
    assert set(dict(f.choices).keys()) == set([3, 7, 12, 16, 18]), (
        'Game.pegi no tiene las opciones esperadas'
    )
    assert not f.blank, 'Game.pegi no debe admitir valores en blanco'

    # category
    assert (f := Game._meta.get_field('category')), 'Game.category no se ha definido'
    assert f.get_internal_type() == 'ForeignKey', 'Game.category no tiene el tipo esperado'
    assert f.related_model._meta.model_name == 'category', (
        'Game.category no referencia al modelo esperado'
    )
    assert f.remote_field.on_delete.__name__ == 'SET_NULL', (
        'Game.category no tiene el método de borrado esperado'
    )
    assert f.null, 'Game.category no admite valores nulos'
    assert f.blank, 'Game.category no admite valores en blanco'
    assert f.remote_field.related_name == 'games', 'Game.category no tiene el related_name esperado'

    # platforms
    assert (f := Game._meta.get_field('platforms')), 'Game.platforms no se ha definido'
    assert f.get_internal_type() == 'ManyToManyField', 'Game.platforms no tiene el tipo esperado'
    assert f.related_model._meta.model_name == 'platform', (
        'Game.platforms no referencia al modelo esperado'
    )
    assert f.remote_field.related_name == 'games', (
        'Game.platforms no tiene el related_name esperado'
    )
    assert not f.blank, 'Game.platforms no debe admitir valores en blanco'


# ==============================================================================
# Review Model
# ==============================================================================


@pytest.mark.score(2)
@pytest.mark.django_db
def test_review_model_is_correctly_configured():
    # rating
    assert (f := Review._meta.get_field('rating')), 'Review.rating no se ha definido'
    assert f.get_internal_type() == 'PositiveSmallIntegerField', (
        'Review.rating no tiene el tipo esperado'
    )
    validators = {v.__class__.__name__: v for v in f.validators}
    assert 'MinValueValidator' in validators, (
        'Review.rating no tiene un validador para el valor mínimo'
    )
    assert validators['MinValueValidator'].limit_value == 1, (
        'Review.rating no tiene el valor mínimo esperado'
    )
    assert 'MaxValueValidator' in validators, (
        'Review.rating no tiene un validador para el valor máximo'
    )
    assert validators['MaxValueValidator'].limit_value == 5, (
        'Review.rating no tiene el valor máximo esperado'
    )
    assert not f.blank, 'Review.rating no debe admitir valores en blanco'

    # comment
    assert (f := Review._meta.get_field('comment')), 'Review.comment no se ha definido'
    assert f.get_internal_type() == 'CharField', 'Review.comment no tiene el tipo esperado'
    assert not f.blank, 'Review.comment no debe admitir valores en blanco'

    # game
    assert (f := Review._meta.get_field('game')), 'Review.game no se ha definido'
    assert f.get_internal_type() == 'ForeignKey', 'Review.game no tiene el tipo esperado'
    assert f.related_model._meta.model_name == 'game', (
        'Review.game no referencia al modelo esperado'
    )
    assert f.remote_field.on_delete.__name__ == 'CASCADE', (
        'Review.game no tiene el método de borrado esperado'
    )
    assert f.remote_field.related_name == 'reviews', 'Review.game no tiene el related_name esperado'
    assert not f.blank, 'Review.game no debe admitir valores en blanco'

    # author
    assert (f := Review._meta.get_field('author')), 'Review.author no se ha definido'
    assert f.get_internal_type() == 'ForeignKey', 'Review.author no tiene el tipo esperado'
    assert f.related_model == User, 'Review.author no referencia al modelo esperado'
    assert f.remote_field.on_delete.__name__ == 'CASCADE', (
        'Review.author no tiene el método de borrado esperado'
    )
    assert f.remote_field.related_name == 'reviews', (
        'Review.author no tiene el related_name esperado'
    )
    assert not f.blank, 'Review.author no debe admitir valores en blanco'

    # created_at
    assert (f := Review._meta.get_field('created_at')), 'Review.created_at no se ha definido'
    assert f.get_internal_type() == 'DateTimeField', 'Review.created_at no tiene el tipo esperado'
    assert f.auto_now_add, 'Review.created_at no tiene auto_now_add activado'
    assert not f.auto_now, 'Review.created_at tiene auto_now activado pero no debería'

    # updated_at
    assert (f := Review._meta.get_field('updated_at')), 'Review.updated_at no se ha definido'
    assert f.get_internal_type() == 'DateTimeField', 'Review.updated_at no tiene el tipo esperado'
    assert f.auto_now, 'Review.updated_at no tiene auto_now activado'
    assert not f.auto_now_add, 'Review.updated_at tiene auto_now_add activado pero no debería'


# ==============================================================================
# Category Model
# ==============================================================================


@pytest.mark.score(2)
@pytest.mark.django_db
def test_category_model_is_correctly_configured():
    # name
    assert (f := Category._meta.get_field('name')), 'Category.name no se ha definido'
    assert f.get_internal_type() == 'CharField', 'Category.name no tiene el tipo esperado'
    assert f.unique, 'Category.name no se ha definido como único'
    assert not f.blank, 'Category.name no debe admitir valores en blanco'

    # slug
    assert (f := Category._meta.get_field('slug')), 'Category.slug no se ha definido'
    assert f.get_internal_type() == 'SlugField', 'Category.slug no tiene el tipo esperado'
    assert f.unique, 'Category.slug no se ha definido como único'
    assert not f.blank, 'Category.slug no debe admitir valores en blanco'

    # description
    assert (f := Category._meta.get_field('description')), 'Category.description no se ha definido'
    assert f.get_internal_type() == 'TextField', 'Category.description no tiene el tipo esperado'
    assert f.blank, 'Category.description no admite valores en blanco'

    # color
    assert (f := Category._meta.get_field('color')), 'Category.color no se ha definido'
    assert f.get_internal_type() in ['CharField', 'ColorField'], (
        'Category.color no tiene el tipo esperado'
    )
    assert f.default.lower() == '#ffffff', 'Category.color no tiene el valor por defecto esperado'
    assert f.blank, 'Category.color no admite valores en blanco'


# ==============================================================================
# Platform Model
# ==============================================================================


@pytest.mark.score(2)
@pytest.mark.django_db
def test_platform_model_is_correctly_configured():
    # name
    assert (f := Platform._meta.get_field('name')), 'Platform.name no se ha definido'
    assert f.get_internal_type() == 'CharField', 'Platform.name no tiene el tipo esperado'
    assert f.unique, 'Platform.name no se ha definido como único'
    assert not f.blank, 'Platform.name no debe admitir valores en blanco'

    # slug
    assert (f := Platform._meta.get_field('slug')), 'Platform.slug no se ha definido'
    assert f.get_internal_type() == 'SlugField', 'Platform.slug no tiene el tipo esperado'
    assert f.unique, 'Platform.slug no se ha definido como único'
    assert not f.blank, 'Platform.slug no debe admitir valores en blanco'

    # description
    assert (f := Platform._meta.get_field('description')), 'Platform.description no se ha definido'
    assert f.get_internal_type() == 'TextField', 'Platform.description no tiene el tipo esperado'
    assert f.blank, 'Platform.description no admite valores en blanco'

    # logo
    assert (f := Platform._meta.get_field('logo')), 'Platform.logo no se ha definido'
    assert f.get_internal_type() in ['FileField', 'ImageField'], (
        'Platform.logo no tiene el tipo esperado'
    )
    assert f.upload_to == 'platforms/logos/', 'Platform.logo no tiene la ruta de subida esperada'
    assert f.blank, 'Platform.logo no admite valores en blanco'
    assert f.default == 'platforms/logos/default.png', (
        'Platform.logo no tiene el valor por defecto esperado'
    )


# ==============================================================================
# Order Model
# ==============================================================================


@pytest.mark.score(2)
@pytest.mark.django_db
def test_order_model_is_correctly_configured():
    # status
    assert (f := Order._meta.get_field('status')), 'Order.status no se ha definido'
    assert f.get_internal_type() == 'SmallIntegerField', 'Order.status no tiene el tipo esperado'
    assert f.default == 1, 'Order.status no tiene el valor por defecto esperado'
    assert set(dict(f.choices).keys()) == set([1, 2, 3, -1]), (
        'Order.status no tiene las opciones esperadas'
    )
    assert not f.blank, 'Order.status no debe admitir valores en blanco'

    # key
    assert (f := Order._meta.get_field('key')), 'Order.key no se ha definido'
    assert f.get_internal_type() == 'UUIDField', 'Order.key no tiene el tipo esperado'
    assert f.default == uuid.uuid4, 'Order.key no tiene el valor por defecto esperado'
    assert f.unique, 'Order.key no se ha definido como único'
    assert not f.editable, 'Order.key debería ser no editable'
    assert not f.blank, 'Order.key no debe admitir valores en blanco'

    # user
    assert (f := Order._meta.get_field('user')), 'Order.user no se ha definido'
    assert f.get_internal_type() == 'ForeignKey', 'Order.user no tiene el tipo esperado'
    assert f.related_model == User, 'Order.user no referencia al modelo esperado'
    assert f.remote_field.on_delete.__name__ == 'CASCADE', (
        'Order.user no tiene el método de borrado esperado'
    )
    assert f.remote_field.related_name == 'orders', 'Order.user no tiene el related_name esperado'
    assert not f.blank, 'Order.user no debe admitir valores en blanco'

    # games
    assert (f := Order._meta.get_field('games')), 'Order.games no se ha definido'
    assert f.get_internal_type() == 'ManyToManyField', 'Order.games no tiene el tipo esperado'
    assert f.related_model._meta.model_name == 'game', (
        'Order.games no referencia al modelo esperado'
    )
    assert f.remote_field.related_name == 'orders', 'Order.games no tiene el related_name esperado'
    assert f.blank, 'Order.games no admite valores en blanco'

    # created_at
    assert (f := Order._meta.get_field('created_at')), 'Order.created_at no se ha definido'
    assert f.get_internal_type() == 'DateTimeField', 'Order.created_at no tiene el tipo esperado'
    assert f.auto_now_add, 'Order.created_at no tiene auto_now_add activado'
    assert not f.auto_now, 'Order.created_at tiene auto_now activado pero no debería'

    # updated_at
    assert (f := Order._meta.get_field('updated_at')), 'Order.updated_at no se ha definido'
    assert f.get_internal_type() == 'DateTimeField', 'Order.updated_at no tiene el tipo esperado'
    assert f.auto_now, 'Order.updated_at no tiene auto_now activado'
    assert not f.auto_now_add, 'Order.updated_at tiene auto_now_add activado pero no debería'


# ==============================================================================
# Token Model
# ==============================================================================


@pytest.mark.score(2)
@pytest.mark.django_db
def test_token_model_is_correctly_configured():
    # key
    assert (f := Token._meta.get_field('key')), 'Token.key no se ha definido'
    assert f.get_internal_type() == 'UUIDField', 'Token.key no tiene el tipo esperado'
    assert f.default == uuid.uuid4, 'Token.key no tiene el valor por defecto esperado'
    assert f.unique, 'Token.key no se ha definido como único'
    assert not f.editable, 'Token.key debería ser no editable'

    # user
    assert (f := Token._meta.get_field('user')), 'Token.user no se ha definido'
    assert f.get_internal_type() == 'OneToOneField', 'Token.user no tiene el tipo esperado'
    assert f.related_model == User, 'Token.user no referencia al modelo esperado'
    assert f.remote_field.on_delete.__name__ == 'CASCADE', (
        'Token.user no tiene el método de borrado esperado'
    )

    # created_at
    assert (f := Token._meta.get_field('created_at')), 'Token.created_at no se ha definido'
    assert f.get_internal_type() == 'DateTimeField', 'Token.created_at no tiene el tipo esperado'
    assert f.auto_now_add, 'Token.created_at no tiene auto_now_add activado'
    assert not f.auto_now, 'Token.created_at tiene auto_now activado pero no debería'
