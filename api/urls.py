from django.urls import re_path
from .views import CategoriesView, DiscountsView, PromocodesView, \
    ProductItemsView, RegistrationAPIView, LoginAPIView, AddProductIntoUserBasket, BasketView


urlpatterns = [
    re_path(r'^categories/', CategoriesView.as_view()),
    re_path(r'^discounts/', DiscountsView.as_view()),
    re_path(r'^promocodes/', PromocodesView.as_view()),
    re_path(r'^products/', ProductItemsView.as_view()),
    re_path(r'^register/', RegistrationAPIView.as_view()),
    re_path(r'^login/', LoginAPIView.as_view()),
    re_path(r'^add-product/', AddProductIntoUserBasket.as_view()),
    re_path(r'^get-user-basket/', BasketView.as_view())
]

