from django.urls import path

from order import views

urlpatterns = [
    path("", views.OrdersList.as_view()),
    path("checkout/", views.checkout, name="checkout"),
]
