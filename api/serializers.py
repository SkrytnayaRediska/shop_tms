from rest_framework import serializers
from .models import Category, Discount, Promocode, ProductItem, RegistredUser, Basket, Order, Cashback
from django.contrib.auth import authenticate
import datetime


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class DiscountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'


class PromocodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocode
        fields = '__all__'


class ProductItemsSerializer(serializers.ModelSerializer):
    category = CategoriesSerializer()
    discount = DiscountsSerializer()
    image = serializers.SerializerMethodField()

    def get_image(self, data):
        request = self.context.get("request")
        if data.image:
            return request.build_absolute_uri(data.image.url)
        return None

    class Meta:
        model = ProductItem
        fields = ('id', 'name', 'description', 'count_on_stock',
                  'price', 'category', 'discount', 'image')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistredUser
        fields = ['login', 'phone', 'age', 'sex', ]


class RegistrationSerializer(serializers.ModelSerializer):
    """ Сериализация регистрации пользователя и создания нового. """

    # Убедитесь, что пароль содержит не менее 8 символов, не более 128,
    # и так же что он не может быть прочитан клиентской стороной
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    # Клиентская сторона не должна иметь возможность отправлять токен вместе с
    # запросом на регистрацию. Сделаем его доступным только на чтение.
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = RegistredUser
        # Перечислить все поля, которые могут быть включены в запрос
        # или ответ, включая поля, явно указанные выше.
        fields = ['phone', 'login', 'password', 'token', 'email']

    def create(self, validated_data):
        # Использовать метод create_user, который мы
        # написали ранее, для создания нового пользователя.
        return RegistredUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        phone = data.get('phone', None)
        password = data.get('password', None)

        if phone is None:
            raise serializers.ValidationError('An phone number is required to log in.')

        if password is None:
            raise serializers.ValidationError('A password is required to log in.')

        user = authenticate(username=phone, password=password)

        if user is None:
            raise serializers.ValidationError('A user with this email and password was not found.')

        if not user.is_active:
            raise serializers.ValidationError('This user has been deactivated.')

        return {
            'phone': user.phone,
            'token': user.token
        }


class AddProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    number_of_items = serializers.IntegerField()


class ProductInBasketSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    number_of_items = serializers.IntegerField()


class BasketSerializer(serializers.Serializer):
    products = ProductInBasketSerializer(many=True)
    result_price = serializers.SerializerMethodField()

    def get_result_price(self, data):
        result_price = 0

        for item in data.get('products'):
            if item.get('discount'):
                percent = item.get('discount_percent')
                expire = item.get('discount_expire')
                print(f"{percent=}, {expire=}")

                delta = expire - datetime.datetime.now(datetime.timezone.utc)

                if delta.days >= 0 and delta.seconds >= 0:
                    result_price += (item.get('price') * (100 - percent) / 100) * item.get("number_of_items")
                else:
                    result_price += item.get('price') * item.get('number_of_items')

            else:
                result_price += item.get('price') * item.get('number_of_items')

        return result_price


class CreateOrderSerializer(serializers.ModelSerializer):

    def run_validation(self, data=None):
        return data

    class Meta:
        model = Order
        fields = '__all__'

    def calculate_result_price(self, data):
        product_items_dict = data.get('product_items')
        product_items_ids = product_items_dict.keys()
        product_items = ProductItem.objects.filter(id__in=product_items_ids).values('id', 'name', 'price',
                                                                                    'discount__percent',
                                                                                    'discount__expire',
                                                                                    'discount__allow_to_sum_with_promo')
        result_price = 0
        promocode_name = self.context.get('request').data.get('promocode')
        promocode = Promocode.objects.filter(name=promocode_name).first()
        for item in product_items:
            number_of_items = product_items_dict.get(str(item.get('id')))
            discount = item.get('discount__percent')
            price = item.get('price')

            if discount:
                date_expire = item.get('discount__expire')
                delta = date_expire - datetime.datetime.now(datetime.timezone.utc)
                if delta.days >= 0 and delta.seconds >= 0:
                    if item.get('discount__allow_to_sum_with_promo') and promocode:
                        result_price += (((price * (100 - discount) / 100) * (100 - promocode.percent) / 100) * number_of_items)
                    else:
                        result_price += (price * (100 - discount) / 100) * number_of_items
                else:
                    result_price += price * number_of_items
            else:
                result_price += price * number_of_items

        user = self.context.get('request').user
        cashback = Cashback.objects.all().first()

        use_cashback = data.get('use_cashback')
        if eval(use_cashback):
            if user.cashback_points > cashback.allowed_amount_to_substract \
                    and result_price > cashback.allowed_amount_to_substract:
                result_price -= cashback.allowed_amount_to_substract
            elif result_price > user.cashback_points:
                result_price -= user.cashback_points


        user.cashback_points += result_price * cashback.percent / 100
        user.save()

        return result_price

    def get_result_number_of_items(self, data):
        return sum(data.get('product_items').values())

    def get_user(self):
        request = self.context.get('request')
        return request.user

    def create(self, validated_data):
        validated_data['result_price'] = self.calculate_result_price(validated_data)
        validated_data['result_number_of_items'] = self.get_result_number_of_items(validated_data)
        validated_data['user'] = self.get_user()
        if validated_data.get('promocode'):
            validated_data.pop('promocode')

        validated_data.pop('use_cashback')

        return Order.objects.create(**validated_data)


class DeleteProductSerializer(serializers.Serializer):
    product_item_id = serializers.IntegerField()
