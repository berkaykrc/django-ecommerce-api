import stripe
from django.conf import settings
from rest_framework import permissions, status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Order
from .serializers import OrderReadSerializer, OrderWriteSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def checkout(request):
    print("requested user:", request.user)
    print("is authenticated", request.user.is_authenticated)
    serializer = OrderWriteSerializer(data=request.data)

    if serializer.is_valid():
        if not serializer.validated_data["items"]:
            return Response(
                {
                    "error": "No items in the cart",
                    "items": ["This field cannot be empty."],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        paid_amount = sum(
            item.get("quantity") * item.get("product").price
            for item in serializer.validated_data["items"]
        )

        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(paid_amount * 100),
                currency="usd",
                payment_method=serializer.validated_data["payment_method"],
                payment_method_types=["card"],
                description="Purchase from E-commerce Django",
                metadata={"user_id": request.user.id},
                confirm=True,
            )

            serializer.save(
                user=request.user,
                paid_amount=paid_amount,
                stripe_token=payment_intent.id,
            )

            return Response(
                {
                    "order": serializer.data,
                    "client_secret": payment_intent.client_secret,
                },
                status=status.HTTP_201_CREATED,
            )
        except stripe.error.CardError as e:
            # Card has been declined
            return Response(
                {"error": f"Card error: {e.user_message}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except stripe.error.RateLimitError as _:
            # Too many requests made to the API too quickly
            return Response(
                {"error": "Rate limit error, please try again later"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            return Response(
                {"error": f"Invalid request: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except stripe.error.AuthenticationError as _:
            # Authentication with Stripe's API failed
            return Response(
                {"error": "Authentication with payment processor failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except stripe.error.APIConnectionError as _:
            # Network communication with Stripe failed
            return Response(
                {"error": "Network error, please try again"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except stripe.error.StripeError as _:
            # Generic error
            return Response(
                {"error": "Something went wrong with the payment"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Something went wrong: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrdersList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderReadSerializer(orders, many=True)
        return Response(serializer.data)
