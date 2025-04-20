import json
from typing import Any
from unittest import mock

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def checkout_url() -> str:
    return reverse(viewname="checkout")


@pytest.fixture
def checkout_data(test_product) -> dict[str, Any]:
    """Create valid checkout data using test_product from conftest.py"""
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "address": "Test Address",
        "zipcode": "12345",
        "place": "Test Place",
        "phone": "1234567890",
        "items": [
            {
                "product": test_product.pk,
                "quantity": 2,
                "price": str(test_product.price),
            }
        ],
    }


@pytest.mark.django_db
@mock.patch("stripe.PaymentIntent.create", autospec=True)
def test_stripe_payment_intent_creation(
    mock_paymentintent_create,
    unauthorized_api_client: APIClient,
    checkout_data: dict[str, Any],
    checkout_url: str,
    get_jwt_header: dict[str, str],
) -> None:
    """Test Stripe payment intent creation.

    Args:
        mock_paymentintent_create: Mocked Stripe PaymentIntent.create function
        unauthorized_api_client: API client fixture without authorization
        checkout_data: Dictionary containing checkout form data
        checkout_url: The URL endpoint for checkout
        get_jwt_header: JWT authorization header fixture

    Tests:
        Verifies that a payment intent is created successfully and
        returns the expected 201 Created response.
    """
    from types import SimpleNamespace

    mock_intent = SimpleNamespace(
        **{
            "id": "pi_3MtwBwLkdIwHu7ix28a3tqPa",
            "client_secret": "pi_3MtwBwLkdIwHu7ix28a3tqPa_secret_YrKJUKribcBjcG8HVhfZluoGH",  # noqa: E501
            "status": "succeeded",
            "amount": 20000,
            "currency": "usd",
        }
    )
    mock_paymentintent_create.return_value = mock_intent
    access_token: str = get_jwt_header["access"]
    unauthorized_api_client.credentials(HTTP_AUTHORIZATION=f"JWT {access_token}")
    checkout_data.update({"payment_method": "pm_card_visa"})
    response = unauthorized_api_client.post(
        path=checkout_url,
        data=json.dumps(checkout_data),
        content_type="application/json",
    )
    mock_paymentintent_create.assert_called_once()

    assert response.status_code == status.HTTP_201_CREATED
    assert status.is_success(code=response.status_code)


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames="code, payment_method, http_code",
    argvalues=[
        ("success", "pm_card_visa", status.HTTP_201_CREATED),
        (
            "generic_declined",
            "pm_card_visa_chargeDeclined",
            status.HTTP_400_BAD_REQUEST,
        ),
        (
            "insufficient_funds",
            "pm_card_visa_chargeDeclinedInsufficientFunds",
            status.HTTP_400_BAD_REQUEST,
        ),
        ("lost", "pm_card_visa_chargeDeclinedLostCard", status.HTTP_400_BAD_REQUEST),
        (
            "expired_card",
            "pm_card_chargeDeclinedExpiredCard",
            status.HTTP_400_BAD_REQUEST,
        ),
        (
            "processing_error",
            "pm_card_chargeDeclinedProcessingError",
            status.HTTP_400_BAD_REQUEST,
        ),
    ],
)
def test_stripe_with_payment_methods(
    unauthorized_api_client: APIClient,
    checkout_data: dict[str, str],
    code,
    payment_method,
    http_code,
    get_jwt_header: dict[str, str],
    checkout_url: str,
) -> None:
    """
    Test handling of various Stripe payment method statuses.

    Verifies that successful cards return 201 and problematic cards
    appropriately return 400 responses.
    """
    access_token: str = get_jwt_header["access"]
    unauthorized_api_client.credentials(HTTP_AUTHORIZATION=f"JWT {access_token}")
    checkout_data.update({"payment_method": payment_method})
    response = unauthorized_api_client.post(
        path=checkout_url,
        data=json.dumps(obj=checkout_data),
        content_type="application/json",
    )
    # Verify success
    assert response.status_code == http_code
