from django.conf import settings
from rest_framework import serializers
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from drf_queryfields import QueryFieldsMixin
from .permissions import IsOwner
from .models import Ad, Make, Alert, CarModel

MIN_YEAR = getattr(settings, 'MIN_YEAR', 1990)

__all__ = [
    'AdSerializer',
    'MakeSerializer',
    'AlertSerializer',
    'CarModelSerializer'
]


class AdSerializer(QueryFieldsMixin, serializers.HyperlinkedModelSerializer):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    make = serializers.HyperlinkedRelatedField(
        view_name='make-detail', queryset=Make.objects.all().order_by('name'))
    model = serializers.HyperlinkedRelatedField(
        view_name='model-detail', queryset=CarModel.objects.all().order_by('name'))
    year = serializers.IntegerField(min_value=MIN_YEAR)
    price = serializers.FloatField(min_value=0)
    dealer = serializers.BooleanField()
    posted_at = serializers.DateTimeField()
    post_url = serializers.URLField(allow_null=False, allow_blank=False)
    title_status = serializers.CharField(
        # choices=['clean', 'lien', 'missing', 'parts', 'rebuilt', 'salvage'],
        max_length=20, allow_blank=True, allow_null=True, required=False)
    drive = serializers.CharField(
        # choices=['4wd', 'fwd', 'rwd'],
        max_length=20, allow_blank=True, allow_null=True, required=False)
    fuel = serializers.CharField(
        # choices=['diesel', 'electric', 'gas', 'hybrid'],
        max_length=20, allow_blank=True, allow_null=True, required=False)
    transmission = serializers.CharField(
        # choices=['automatic', 'manual'],
        max_length=20, allow_blank=True, allow_null=True, required=False)
    size = serializers.CharField(
        # choices=['compact', 'sub-compact', 'full-size', 'mid-size'],
        max_length=20, allow_blank=True, allow_null=True, required=False)
    condition = serializers.CharField(
        # choices=['good', 'fair', 'like new', 'excellent', 'new', 'salvage'],
        max_length=20, allow_blank=True, allow_null=True, required=False)
    category = serializers.CharField(
        # choices=['wagon', 'van', 'bus', 'offroad', 'coupe', 'SUV',
        #         'pickup', 'truck', 'mini-van', 'sedan', 'convertible', 'hatchback'],
        max_length=20, allow_blank=True, allow_null=True, required=False)
    color = serializers.CharField(
        # choices=['blue', 'brown', 'purple', 'grey', 'yellow', 'custom',
        #         'black', 'orange', 'green', 'white', 'silver', 'red'],
        max_length=20, allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = Ad
        fields = (
            'url', 'make', 'model', 'year', 'price',
            'title_status', 'odometer', 'size',
            'category', 'color', 'condition',
            'drive', 'fuel', 'transmission',
            'latitude', 'longitude', 'dealer',
            'cylinders', 'posted_at', 'make_name',
            'post_url', 'slug', 'created_at', 'updated_at',
            'predict_price', 'predicted_at', 'title',
            'predict_info',
        )
        read_only_fields = (
            'slug', 'make_name', 'created_at', 'updated_at', 'title',
            'predict_price', 'predicted_at', 'predict_info',
        )


class MakeSerializer(QueryFieldsMixin, serializers.HyperlinkedModelSerializer):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    name = serializers.CharField(max_length=60, trim_whitespace=True)
    models = serializers.HyperlinkedRelatedField(
        view_name='model-detail', many=True, read_only=True)

    class Meta:
        model = Make
        fields = ('url', 'name', 'models', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class CarModelSerializer(QueryFieldsMixin, serializers.HyperlinkedModelSerializer):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    name = serializers.CharField(max_length=60, trim_whitespace=True)
    make = serializers.HyperlinkedRelatedField(
        view_name='make-detail', queryset=Make.objects.all().order_by('name'), lookup_field='pk')

    class Meta:
        model = CarModel
        extra_kwargs = {'url': {'view_name': 'model-detail'}}
        fields = ('url', 'name', 'make', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class AlertSerializer(QueryFieldsMixin, serializers.HyperlinkedModelSerializer):
    authentication_classes = [BasicAuthentication, SessionAuthentication, TokenAuthentication]
    permission_classes = (IsOwner,)
    min_year = serializers.IntegerField(min_value=MIN_YEAR)
    max_year = serializers.IntegerField(min_value=MIN_YEAR)
    min_price = serializers.IntegerField(min_value=0)
    max_price = serializers.IntegerField(min_value=0)
    title_status = serializers.ChoiceField(
        choices=['clean', 'lien', 'missing', 'parts', 'rebuilt', 'salvage'],
        allow_blank=True)
    enabled = serializers.BooleanField(default=False)
    slack_web_hook = serializers.URLField()

    class Meta:
        model = Alert
        fields = (
            'url', 'min_year', 'max_year', 'owner',
            'min_price', 'max_price', 'title_status', 'enabled',
            'slack_web_hook', 'created_at', 'updated_at'
        )
        read_only_fields = ('owner', 'created_at', 'updated_at')
