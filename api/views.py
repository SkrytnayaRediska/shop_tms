# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, get_list_or_404
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Category, Discount, ProductItem, Promocode, RegistredUser
from .serializers import CategoriesSerializer, DiscountsSerializer, \
    PromocodesSerializer, ProductItemsSerializer, UserSerializer, LoginSerializer, RegistrationSerializer


class CategoriesView(ListAPIView):
    queryset = get_list_or_404(Category)
    serializer_class = CategoriesSerializer


class DiscountsView(ListAPIView):
    queryset = get_list_or_404(Discount)
    serializer_class = DiscountsSerializer


class PromocodesView(ListAPIView):
    queryset = get_list_or_404(Promocode)
    serializer_class = PromocodesSerializer


class ProductItemsView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = get_list_or_404(ProductItem)
    serializer_class = ProductItemsSerializer


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
        serializer.save()

        return Response(serializer.data, status=200)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Обратите внимание, что мы не вызываем метод save() сериализатора, как
        # делали это для регистрации. Дело в том, что в данном случае нам
        # нечего сохранять. Вместо этого, метод validate() делает все нужное.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=200)

