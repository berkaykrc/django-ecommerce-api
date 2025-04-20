from typing import Any, Generator

import pytest
import stripe
from django.conf import settings
from django.contrib.auth.models import User
from product.models import Category, Product
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture(scope="function")
def unauthorized_api_client() -> Generator[APIClient, Any, None]:
    """Fixture to provide client"""
    yield APIClient()


@pytest.fixture
def api_client_with_credentials(
    unauthorized_api_client: APIClient, test_user: User
) -> Generator[APIClient, Any, None]:
    """Fixture to provide an authenticated API client using the provided test user."""
    unauthorized_api_client.force_authenticate(user=test_user)
    yield unauthorized_api_client
    unauthorized_api_client.force_authenticate(user=None)


@pytest.fixture
def get_jwt_header(test_user: User) -> dict[str, str]:
    """Generate JWT authentication header for a test user.
    Args:
        test_user : User The user instance for which to generate the JWT tokens
    Returns: dict
        A dictionary containing 'refresh' and 'access' token strings that can be
        used for authentication in tests
    """

    refresh: RefreshToken = RefreshToken.for_user(test_user)

    return {"refresh": str(refresh), "access": str(refresh.access_token)}


@pytest.fixture(scope="session", autouse=True)
def configure_stripe() -> None:
    """Configure Stripe with API key from settings for all tests"""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    # Verify the API key is valid and configured
    try:
        stripe.Account.retrieve()
        print("Stripe API connection successful")
    except Exception as e:
        print(f"Warning: Stripe API configuration issue: {e}")


@pytest.fixture
def test_user() -> User:
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpassword123"
    )


@pytest.fixture
def test_category() -> Category:
    return Category.objects.create(name="Test Category")


@pytest.fixture
def test_product(test_category: Category) -> Product:
    return Product.objects.create(
        category=test_category,
        name="Test Product",
        slug="test-product",
        description="Test description",
        price=100.00,
    )
