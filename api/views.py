# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, get_list_or_404

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.views import APIView
from django.db.models import F
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .models import Category, Discount, ProductItem, Promocode, RegistredUser, Basket
from .tasks import send_email_confirmation
from .serializers import CategoriesSerializer, DiscountsSerializer, \
    PromocodesSerializer, ProductItemsSerializer, UserSerializer, LoginSerializer, RegistrationSerializer, \
    AddProductSerializer, BasketSerializer, CreateOrderSerializer, DeleteProductSerializer

from drf_yasg.utils import swagger_auto_schema


class CategoriesView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class DiscountsView(ListAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountsSerializer


"""class PromocodesView(ListAPIView):
    queryset = get_list_or_404(Promocode)
    serializer_class = PromocodesSerializer


class ProductItemsView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = get_list_or_404(ProductItem)
    serializer_class = ProductItemsSerializer"""


class RegistrationAPIView(APIView):
    """
    Разрешить всем пользователям (аутентифицированным и нет) доступ к данному эндпоинту.
    """
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Паттерн создания сериализатора, валидации и сохранения - довольно
        # стандартный, и его можно часто увидеть в реальных проектах.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        current_site = get_current_site(request)
        send_email_confirmation.delay(user.id, current_site.domain)

        return Response(serializer.data, status=200)


class ActivateAccountView(APIView):

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = RegistredUser.objects.get(pk=uid)
        except Exception as e:
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response('Thank you for your email confirmation. Now you can login your account.', status=200)
        else:
            return Response('Activation link is invalid!', status=403)



class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        request_body=LoginSerializer,
        request_method='POST',
        responses={
            200: LoginSerializer
        }
    )
    def post(self, request):
        user = request.data.get('user', {})

        # Обратите внимание, что мы не вызываем метод save() сериализатора, как
        # делали это для регистрации. Дело в том, что в данном случае нам
        # нечего сохранять. Вместо этого, метод validate() делает все нужное.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=200)

"""class AddProductIntoUserBasket(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        input_serializer = AddProductSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        product = get_object_or_404(ProductItem, id=input_serializer.data.get("product_id"))

        object, created = Basket.objects.get_or_create(user=request.user, product=product)
        if object.number_of_items:
            object.number_of_items += input_serializer.data.get("number_of_items")
        else:
            object.number_of_items = input_serializer.data.get("number_of_items")
        object.save()

        return Response(status=200)


class DeleteProductFromUserBasket(APIView):
    permission_classes = (IsAuthenticated, )

    def delete(self, request):
        user = request.user
        serializer = DeleteProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_item = get_object_or_404(ProductItem, id=serializer.data.get('product_item_id'))
        Basket.objects.get(user=user, product=product_item).delete()

        return Response(status=200)"""




class BasketView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        basket = ProductItem.objects.prefetch_related("basket_set").filter(basket__user=user)\
            .values("name", "price", "discount", number_of_items=F("basket__number_of_items"),
                    discount_percent=F("discount__percent"), discount_expire=F("discount__expire"))

        serializer = BasketSerializer({"products": basket})

        return Response(serializer.data, status=200)


class CreateOrderView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=CreateOrderSerializer,
        request_method='POST',
        responses={
            200: CreateOrderSerializer
        }
    )
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        return Response(serializer.data, status=200)

