from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


def get_user_jwt_header(username, password):
    """
    Get JWT authorization header for a user.

    Args:
        username: The username to authenticate
        password: The user's password

    Returns:
        Dictionary containing the authorization header with JWT token
    """
    client = APIClient()
    response = client.post(
        reverse(
            "jwt-create"
        ),  # Use the appropriate URL name for the JWT token endpoint
        {"username": username, "password": password},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK, (
        f"Login failed: {response.content}"
    )

    jwt = response.data["access"]  # Get the access token from the response

    return {
        "Authorization": f"JWT {jwt}",
    }
