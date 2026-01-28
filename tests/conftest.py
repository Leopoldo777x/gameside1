import pytest

from factories import (
    CategoryFactory,
    GameFactory,
    OrderFactory,
    PlatformFactory,
    ReviewFactory,
    TokenFactory,
    UserFactory,
)

# ==============================================================================
# SCORE
# ==============================================================================


DEFAULT_SCORE = 1
TOTAL_SCORE = 0
MAX_SCORE = 0


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, *args, **kwargs):
    global TOTAL_SCORE, MAX_SCORE

    outcome = yield
    rep = outcome.get_result()

    # Solo evaluamos el resultado final del test
    if rep.when != 'call':
        return

    if marker := item.get_closest_marker('score'):
        score = marker.args[0]
    else:
        score = DEFAULT_SCORE

    # El score máximo siempre cuenta
    MAX_SCORE += score

    # El score obtenido solo si pasa
    if rep.passed:
        TOTAL_SCORE += score


def pytest_sessionfinish(*args, **kwargs):
    SEP_WIDTH = 30

    print('\n\n' + '=' * SEP_WIDTH)
    print('🏁 RESULTADO FINAL')
    print(f'✅ Score obtenido: {TOTAL_SCORE}')
    print(f'📊 Score máximo:   {MAX_SCORE}')

    if MAX_SCORE > 0:
        percentage = (TOTAL_SCORE / MAX_SCORE) * 100
        percentage_r = round(TOTAL_SCORE / MAX_SCORE, 1) * 100
        print(f'📈 Porcentaje:     {percentage:.2f}%')
        print(f'📝 Porcentaje (R): {percentage_r:.0f}%')

    print('=' * SEP_WIDTH)


# ==============================================================================
# URL Patterns
# ==============================================================================

CATEGORY_LIST_URL = '/api/categories/'
CATEGORY_DETAIL_URL = '/api/categories/{category_slug}/'

GAME_LIST_URL = '/api/games/'
GAME_FILTER_URL = '/api/games/?category={category_slug}&platform={platform_slug}'
GAME_DETAIL_URL = '/api/games/{game_slug}/'

REVIEW_LIST_URL = '/api/games/{game_slug}/reviews/'
REVIEW_DETAIL_URL = '/api/games/reviews/{review_pk}/'
REVIEW_ADD_URL = '/api/games/{game_slug}/reviews/add/'

ORDER_ADD_URL = '/api/orders/add/'
ORDER_DETAIL_URL = '/api/orders/{order_pk}/'
ORDER_GAME_LIST_URL = '/api/orders/{order_pk}/games/'
ORDER_ADD_GAME_URL = '/api/orders/{order_pk}/games/add/'
ORDER_STATUS_URL = '/api/orders/{order_pk}/status/'
ORDER_PAY_URL = '/api/orders/{order_pk}/pay/'

PLATFORM_LIST_URL = '/api/platforms/'
PLATFORM_DETAIL_URL = '/api/platforms/{platform_slug}/'

AUTH_URL = '/api/auth/'


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture(autouse=True)
def media_tmpdir(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / 'media'


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def token(user):
    return TokenFactory(user=user)


@pytest.fixture
def order(user):
    return OrderFactory(user=user)


@pytest.fixture
def game():
    return GameFactory()


@pytest.fixture
def category():
    return CategoryFactory()


@pytest.fixture
def platform():
    return PlatformFactory()


@pytest.fixture
def review(user, game):
    return ReviewFactory(author=user, game=game)
