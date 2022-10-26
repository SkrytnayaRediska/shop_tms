from django.urls import re_path, path
from .views import CategoriesView, DiscountsView, PromocodesView, \
    ProductItemsView, RegistrationAPIView, LoginAPIView, AddProductIntoUserBasket, \
    BasketView, CreateOrderView, ActivateAccountView, DeleteProductFromUserBasket


urlpatterns = [
    re_path(r'^categories/', CategoriesView.as_view()),
    re_path(r'^discounts/', DiscountsView.as_view()),
    re_path(r'^promocodes/', PromocodesView.as_view()),
    re_path(r'^products/', ProductItemsView.as_view()),
    re_path(r'^register/', RegistrationAPIView.as_view()),
    re_path(r'^login/', LoginAPIView.as_view()),
    re_path(r'^add-product/', AddProductIntoUserBasket.as_view()),
    re_path(r'^get-user-basket/', BasketView.as_view()),
    re_path(r'^create-order/', CreateOrderView.as_view()),
    re_path(r'^delete-product/', DeleteProductFromUserBasket.as_view()),
    path('activate/<slug:uidb64>/<slug:token>/', ActivateAccountView.as_view(), name='activate')
]


