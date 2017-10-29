from django.conf.urls import url, include
from rest_framework.authtoken import views as drf_views
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'ads', views.AdViewSet)
router.register(r'makes', views.MakeViewSet)
router.register(r'models', views.CarModelViewSet, base_name='model')
router.register(r'alerts', views.AlertViewSet)


urlpatterns = [
    url(r'^auth$', drf_views.obtain_auth_token, name='auth'),
    url(r'^', include(router.urls)),
]
