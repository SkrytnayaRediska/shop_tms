from rest_framework import serializers
from .models import Category, Discount, Promocode, ProductItem, RegistredUser
from django.contrib.auth import authenticate


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
        fields = ['phone', 'login', 'password', 'token']

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
            raise serializers.ValidationError('An phone address is required to log in.')

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