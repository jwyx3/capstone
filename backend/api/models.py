from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.signals import pre_save
from django.contrib.auth.models import User
from .utils import unique_slug_generator

MIN_YEAR = getattr(settings, 'MIN_YEAR', 1990)


class Make(models.Model):
    name = models.CharField(max_length=60, null=False, blank=False, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


def make_rl_pre_save_receiver(sender, instance, *args, **kwargs):
    instance.name = ' '.join(x.capitalize() for x in instance.name.split('-'))


pre_save.connect(make_rl_pre_save_receiver, sender=Make)


class CarModel(models.Model):
    name = models.CharField(max_length=60, null=False, blank=False, db_index=True)
    make = models.ForeignKey(Make, null=False, blank=False,
                             on_delete=models.CASCADE, related_name='models',
                             related_query_name='model')
    predict_model = models.CharField(max_length=120, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Alert(models.Model):
    owner = models.ForeignKey(User, null=False, blank=False, db_index=True)
    slack_web_hook = models.URLField(max_length=1024, null=True, blank=True, db_index=True)
    car_models = models.ManyToManyField(CarModel, related_name='models', related_query_name='model')
    min_year = models.SmallIntegerField(validators=[MinValueValidator(MIN_YEAR)], null=True, blank=True)
    max_year = models.SmallIntegerField(validators=[MinValueValidator(MIN_YEAR)], null=True, blank=True)
    min_price = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    max_price = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    title_status = models.CharField(max_length=20, null=True, blank=True)
    enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_enabled(self):
        return ('disabled', 'enabled')[self.enabled]


class Ad(models.Model):
    make = models.ForeignKey(Make, null=False, blank=False, db_index=True)
    model = models.ForeignKey(CarModel, null=False, blank=False, db_index=True)
    year = models.SmallIntegerField(null=False, blank=False, validators=[MinValueValidator(MIN_YEAR)], db_index=True)
    price = models.FloatField(null=False, blank=False, validators=[MinValueValidator(0)], db_index=True)
    odometer = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    dealer = models.BooleanField(null=False, blank=False)
    posted_at = models.DateTimeField(null=False, blank=False, db_index=True)
    post_url = models.URLField(null=False, blank=False, unique=True, db_index=True)

    title_status = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    drive = models.CharField(max_length=20, null=True, blank=True)
    fuel = models.CharField(max_length=20, null=True, blank=True)
    transmission = models.CharField(max_length=20, null=True, blank=True)
    size = models.CharField(max_length=20, null=True, blank=True)
    condition = models.CharField(max_length=20, null=True, blank=True)
    category = models.CharField(max_length=20, null=True, blank=True)
    color = models.CharField(max_length=20, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    cylinders = models.SmallIntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    predict_price = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    predict_info = models.CharField(max_length=120, null=True, blank=True)
    predicted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def make_name(self):
        return self.make.name

    @property
    def model_name(self):
        return self.model.name

    @property
    def title(self):
        return "{0.year} {0.make} {0.model} - ${0.price}".format(self)

    def __str__(self):
        return self.title


def ad_rl_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(ad_rl_pre_save_receiver, sender=Ad)
