# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
#
#
# class ATests(APITestCase):
#     def test_if_two_is_two(self):
#         self.assertEqual(2, 2)
#
#     def test_index_loads_properly(self):
#         """The index page loads properly"""
#         response = self.client.get('127.0.0.1:8000')
#         self.assertEqual(response.status_code, 404)
#
# from django.test import TestCase, RequestFactory
# from ..models import Category
# from ..views import CategoriesView
#
# class MyTest(TestCase):
#     fixtures = ['api/tests/fixtures/fixture_1.json']
#
#     def setUp(self):
#         # Every test needs access to the request factory.
#         self.factory = RequestFactory()
#
#     def test_should_create_group(self):
#         category = Category.objects.get(id=1)
#         self.assertEqual(category.name, "cat1")
#
#         request = self.factory.get('/api/categories/')
#         response = CategoriesView.as_view()(request)
#         self.assertEqual(response.status_code, 200)
#         self.assertIsInstance(response.data, list)
#
#
# from django.urls import include, path, reverse
# from rest_framework.test import APITestCase, URLPatternsTestCase
#
#
# class AccountTests(APITestCase, URLPatternsTestCase):
#     urlpatterns = [
#         path('api/', include('api.urls')),
#     ]
#     fixtures = ['api/tests/fixtures/fixture_1.json']
#
#     def test_create_account(self):
#         """
#         Ensure we can create a new account object.
#         """
#         url = reverse('categories')
#         response = self.client.get(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 2)





from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APITestCase
from ..views import CategoriesView


class FirstSimpleTest(APITestCase):
    fixtures = ['api/tests/fixtures/fixture_1.json']

    def setUp(self):
        self.factory = RequestFactory()

    def test_categories_view(self):
        url = reverse('categories')
        response = self.client.get(url, format='json')
        self.assertIsInstance(response.data, list)
        self.assertEqual(response.data[0]['name'], 'cat1')
        self.assertEqual(response.data[1]['name'], 'cat2')
        self.assertEqual(len(response.data), 2)
        request = self.factory.get(url)
        response = CategoriesView.as_view()(request)
        self.assertIsInstance(response.data, list)

    def test_discounts_view(self):
        url = reverse('discounts')
        response = self.client.get(url, format='json')
        self.assertIsInstance(response.data, list)
        self.assertEqual(response.data[0]['name'], 'disc1')
        self.assertEqual(response.data[1]['name'], 'disc2')
        self.assertEqual(len(response.data), 2)













