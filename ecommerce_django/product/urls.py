from django.urls import path, include

from product import views

urlpatterns = [

    path('latest-products/', views.LastestProductsList.as_view()),
    path('product/search/', views.search),
    path('product/<slug:category_slug>/<slug:product_slug>/',
         views.ProductDetail.as_view()),
    path('product/<slug:category_slug>/', views.CategoryDetail.as_view())

]
