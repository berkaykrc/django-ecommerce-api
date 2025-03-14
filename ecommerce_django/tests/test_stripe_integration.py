import json
from unittest.mock import MagicMock, patch

import pytest
import stripe
from django.urls import reverse
from order.views import checkout
from rest_framework.test import APIRequestFactory


# Use pytest fixtures instead of setUp method
@pytest.fixture
def api_factory():
    return APIRequestFactory()


@pytest.fixture
def checkout_url():
    return reverse("checkout")


@pytest.fixture
def checkout_data(test_product):
    """Create valid checkout data using test_product from conftest.py"""
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "address": "Test Address",
        "zip_code": "12345",
        "place": "Test Place",
        "phone": "1234567890",
        "items": [
            {
                "product": test_product.id,
                "quantity": 2,
                "price": str(test_product.price),
            }
        ],
        "payment_method": {
            "card": {
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": 2030,
                "cvc": "123",
            },
            "billing_details": {"postal_code": "12345"},
        },
    }


# Convert class-based tests to pytest function-based tests
@patch("stripe.PaymentIntent.create")
@patch("product.models.Product.objects.get")
def test_stripe_payment_intent_creation(
    mock_product_get,
    mock_payment_intent,
    test_user,
    test_product,
    api_factory,
    checkout_data,
):
    # Mock the product
    mock_product = MagicMock()
    mock_product.price = 100.00
    mock_product.id = test_product.id
    mock_product_get.return_value = mock_product

    # Mock the Stripe PaymentIntent.create method
    mock_intent = MagicMock()
    mock_intent.id = "pi_test_123456789"
    mock_intent.client_secret = "cs_test_123456789"
    mock_payment_intent.return_value = mock_intent

    # Create request
    request = api_factory.post(
        "/api/checkout/",
        data=json.dumps(checkout_data),
        content_type="application/json",
    )
    request.user = test_user

    # Call the checkout view
    response = checkout(request)

    # Verify PaymentIntent.create was called with correct amount
    mock_payment_intent.assert_called_once()
    call_kwargs = mock_payment_intent.call_args[1]
    assert call_kwargs["amount"] == 20000  # $200 = 2 * $100
    assert call_kwargs["currency"] == "usd"
    assert response.status_code == 201


@patch("stripe.PaymentIntent.create")
@patch("product.models.Product.objects.get")
def test_stripe_with_successful_card(
    mock_product_get,
    mock_payment_intent,
    test_user,
    test_product,
    api_factory,
    checkout_data,
    test_cards,
):
    # Mock the product
    mock_product = MagicMock()
    mock_product.price = 100.00
    mock_product.id = test_product.id
    mock_product_get.return_value = mock_product

    # Use successful test card
    checkout_data["payment_method"]["card"]["number"] = test_cards["success"]

    # Mock the Stripe PaymentIntent.create method for success
    mock_intent = MagicMock()
    mock_intent.id = "pi_test_success"
    mock_intent.client_secret = "cs_test_success"
    mock_payment_intent.return_value = mock_intent

    # Create request
    request = api_factory.post(
        "/api/checkout/",
        data=json.dumps(checkout_data),
        content_type="application/json",
    )
    request.user = test_user

    # Call the checkout view
    response = checkout(request)

    # Verify success
    assert response.status_code == 201


@patch("stripe.PaymentIntent.create")
@patch("product.models.Product.objects.get")
def test_stripe_with_declined_card(
    mock_product_get,
    mock_payment_intent,
    test_user,
    test_product,
    api_factory,
    checkout_data,
    test_cards,
):
    # Mock the product
    mock_product = MagicMock()
    mock_product.price = 100.00
    mock_product.id = test_product.id
    mock_product_get.return_value = mock_product

    # Use declined test card
    checkout_data["payment_method"]["card"]["number"] = test_cards["declined"]

    # Mock the Stripe CardError for declined card
    mock_payment_intent.side_effect = stripe.error.CardError(
        param="card",
        code="card_declined",
        message="Your card was declined.",
        json_body={
            "error": {"code": "card_declined", "message": "Your card was declined."}
        },
    )

    # Create request
    request = api_factory.post(
        "/api/checkout/",
        data=json.dumps(checkout_data),
        content_type="application/json",
    )
    request.user = test_user

    # Call the checkout view
    response = checkout(request)

    # Verify declined
    assert response.status_code == 400
    assert "error" in response.data


@patch("stripe.PaymentIntent.confirm")
@patch("stripe.PaymentIntent.create")
@patch("product.models.Product.objects.get")
def test_stripe_3ds_authentication(
    mock_product_get,
    mock_create,
    mock_confirm,
    test_user,
    test_product,
    api_factory,
    checkout_data,
    test_cards,
):
    # Mock the product
    mock_product = MagicMock()
    mock_product.price = 100.00
    mock_product.id = test_product.id
    mock_product_get.return_value = mock_product

    # Set card that requires authentication
    checkout_data["payment_method"]["card"]["number"] = test_cards["requires_auth"]

    # Mock the initial payment intent creation
    mock_intent = MagicMock()
    mock_intent.id = "pi_test_auth"
    mock_intent.client_secret = "cs_test_auth"
    mock_intent.status = "requires_action"
    mock_intent.next_action = {
        "type": "use_stripe_sdk",
        "use_stripe_sdk": {"type": "3d_secure_redirect"},
    }
    mock_create.return_value = mock_intent

    # Create request
    request = api_factory.post(
        "/api/checkout/",
        data=json.dumps(checkout_data),
        content_type="application/json",
    )
    request.user = test_user

    # Call the checkout view
    response = checkout(request)

    # Verify response contains authentication info
    assert response.status_code == 200
    assert "requires_action" in response.data
    assert "payment_intent_client_secret" in response.data


@patch("stripe.PaymentIntent.create")
@patch("product.models.Product.objects.get")
def test_stripe_card_error_handling(
    mock_product_get,
    mock_payment_intent,
    test_user,
    test_product,
    api_factory,
    checkout_data,
):
    # Mock the product
    mock_product = MagicMock()
    mock_product.price = 100.00
    mock_product.id = test_product.id
    mock_product_get.return_value = mock_product

    # Mock Stripe CardError
    mock_payment_intent.side_effect = stripe.error.CardError(
        param="number", code="invalid_number", message="Your card number is invalid"
    )

    # Create request
    request = api_factory.post(
        "/api/checkout/",
        data=json.dumps(checkout_data),
        content_type="application/json",
    )
    request.user = test_user

    # Call the checkout view
    response = checkout(request)

    # Verify error response
    assert response.status_code == 400
    assert "error" in response.data
    assert "card" in response.data["error"].lower()


@patch("stripe.PaymentIntent.create")
@patch("product.models.Product.objects.get")
def test_stripe_rate_limit_error_handling(
    mock_product_get,
    mock_payment_intent,
    test_user,
    test_product,
    api_factory,
    checkout_data,
):
    # Mock the product
    mock_product = MagicMock()
    mock_product.price = 100.00
    mock_product.id = test_product.id
    mock_product_get.return_value = mock_product

    # Mock Stripe RateLimitError
    mock_payment_intent.side_effect = stripe.error.RateLimitError(
        message="Too many requests made to the API too quickly"
    )

    # Create request
    request = api_factory.post(
        "/api/checkout/",
        data=json.dumps(checkout_data),
        content_type="application/json",
    )
    request.user = test_user

    # Call the checkout view
    response = checkout(request)

    # Verify error response
    assert response.status_code == 400
    assert "error" in response.data
    assert "rate limit" in response.data["error"].lower()


@patch("stripe.PaymentIntent.create")
@patch("product.models.Product.objects.get")
def test_stripe_authentication_error_handling(
    mock_product_get,
    mock_payment_intent,
    test_user,
    test_product,
    api_factory,
    checkout_data,
):
    # Mock the product
    mock_product = MagicMock()
    mock_product.price = 100.00
    mock_product.id = test_product.id
    mock_product_get.return_value = mock_product

    # Mock Stripe AuthenticationError
    mock_payment_intent.side_effect = stripe.error.AuthenticationError(
        message="Invalid API Key provided"
    )

    # Create request
    request = api_factory.post(
        "/api/checkout/",
        data=json.dumps(checkout_data),
        content_type="application/json",
    )
    request.user = test_user

    # Call the checkout view
    response = checkout(request)

    # Verify error response
    assert response.status_code == 400
    assert "error" in response.data
    assert "authentication" in response.data["error"].lower()


@patch("stripe.PaymentIntent.create")
@patch("product.models.Product.objects.get")
def test_generic_stripe_error_handling(
    mock_product_get,
    mock_payment_intent,
    test_user,
    test_product,
    api_factory,
    checkout_data,
):
    # Mock the product
    mock_product = MagicMock()
    mock_product.price = 100.00
    mock_product.id = test_product.id
    mock_product_get.return_value = mock_product

    # Mock generic Stripe error
    mock_payment_intent.side_effect = stripe.error.StripeError(
        message="Something unexpected went wrong"
    )

    # Create request
    request = api_factory.post(
        "/api/checkout/",
        data=json.dumps(checkout_data),
        content_type="application/json",
    )
    request.user = test_user

    # Call the checkout view
    response = checkout(request)

    # Verify error response
    assert response.status_code == 400
    assert "error" in response.data
