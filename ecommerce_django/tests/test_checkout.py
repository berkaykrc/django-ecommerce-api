import json

from django.contrib.auth.models import User
from django.urls import reverse
from order.models import Order
from product.models import Category, Product
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ecommerce_django.tests.utils.api_token import get_user_jwt_header


class CheckoutEndpointTest(APITestCase):
    def setUp(self):
        username = "testuser"
        email = "test@example.com"
        password = "testpassword123"
        # Create a test user
        self.user = User.objects.create_user(
            username=username, email=email, password=password
        )

        # Create a test category
        self.category = Category.objects.create(name="Test Category")

        # Create a test product
        self.product = Product.objects.create(
            category=self.category,
            name="Test Product",
            slug="test-product",
            description="Test description",
            price=100.00,
        )

        # Setup client
        self.client = APIClient()
        # self.client.force_authenticate(user=self.user)
        self.jwt_token = get_user_jwt_header(username, password)["Authorization"]
        self.client.credentials(HTTP_AUTHORIZATION=self.jwt_token)
        self.checkout_url = reverse("checkout")

        # Valid checkout data
        self.checkout_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "address": "Test Address",
            "zipcode": "12345",
            "place": "Test Place",
            "phone": "1234567890",
            "items": [
                {
                    "product": self.product.pk,
                    "quantity": 2,
                    "price": str(self.product.price),
                }
            ],
            "payment_method": "pm_card_visa",
        }

    def test_successful_checkout(self):
        # Make the checkout request with successful card
        response = self.client.post(
            self.checkout_url,
            data=json.dumps(self.checkout_data),
            content_type="application/json",
        )

        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify order was created
        self.assertTrue(
            Order.objects.filter(
                user=self.user, first_name="Test", last_name="User"
            ).exists()
        )

        # Verify order has items
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.items.count(), 1)

        # Verify payment details (stripe_token should be present)
        self.assertTrue(order.stripe_token)

    def test_checkout_with_invalid_data(self):
        # Invalid data missing required fields
        invalid_data = {
            "first_name": "Test",
            # Missing last_name and other required fields
            "items": [{"product": self.product.pk, "quantity": 2}],
        }

        # Make the checkout request
        response = self.client.post(
            self.checkout_url,
            data=json.dumps(invalid_data),
            content_type="application/json",
        )

        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify no order was created
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_with_empty_cart(self):
        # Checkout data with empty items
        empty_cart_data = self.checkout_data
        empty_cart_data["items"] = []
        # Make the checkout request
        response = self.client.post(
            self.checkout_url,
            data=json.dumps(empty_cart_data),
            content_type="application/json",
        )

        # Check response (should fail with bad request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify no order was created
        self.assertEqual(Order.objects.count(), 0)

        # Check for error message related to empty cart
        self.assertIn("items", response.data)

    def test_checkout_unauthenticated(self):
        # Logout the user
        self.client.logout()
        # Make the checkout request
        response = self.client.post(
            self.checkout_url,
            data=json.dumps(self.checkout_data),
            content_type="application/json",
        )

        # Check response - should require authentication
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_checkout_with_declined_card(self):
        # Checkout data with a card that will be declined
        declined_card_data = self.checkout_data.copy()
        declined_card_data["payment_method"] = "pm_card_visa_chargeDeclined"

        # Make the checkout request with declined card
        response = self.client.post(
            self.checkout_url,
            data=json.dumps(declined_card_data),
            content_type="application/json",
        )

        # Check response (should indicate error)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(response.data)
        # Verify no order was created
        self.assertEqual(Order.objects.count(), 0)
