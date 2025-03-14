import pytest
import stripe
from django.conf import settings
from django.contrib.auth.models import User
from product.models import Category, Product


@pytest.fixture(scope="session", autouse=True)
def configure_stripe():
    """Configure Stripe with API key from settings for all tests"""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    # Verify the API key is valid and configured
    try:
        stripe.Account.retrieve()
        print("Stripe API connection successful")
    except Exception as e:
        print(f"Warning: Stripe API configuration issue: {e}")


@pytest.fixture
def test_user():
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpassword123"
    )


@pytest.fixture
def test_category():
    return Category.objects.create(name="Test Category")


@pytest.fixture
def test_product(test_category):
    return Product.objects.create(
        category=test_category,
        name="Test Product",
        slug="test-product",
        description="Test description",
        price=100.00,
    )


@pytest.fixture
def test_cards():
    """Fixture providing Stripe test card numbers for various scenarios"""
    return {
        "success": "4242424242424242",  # Succeeds and immediately processes the payment
        "requires_auth": "4000002500003155",  # Requires authentication
        "declined": "4000000000000002",  # Always declined
        "insufficient_funds": "4000000000009995",  # Declined for insufficient funds
        "incorrect_cvc": "4000000000000127",  # Declined for incorrect CVC
        "expired_card": "4000000000000069",  # Declined for expired card
        "processing_error": "4000000000000119",  # Declined for processing error
    }


@pytest.fixture
def payment_method_data():
    """Fixture providing standard payment method data for tests"""
    return {
        "card": {
            "number": "4242424242424242",  # Default to successful card
            "exp_month": 12,
            "exp_year": 2030,  # Future year
            "cvc": "123",  # Any 3-digit number
        },
        "billing_details": {
            "postal_code": "12345"  # Any postal code
        },
    }
