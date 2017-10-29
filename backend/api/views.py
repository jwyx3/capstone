from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import list_route
from django.db.models import Count
from .models import CarModel, Ad, Make, Alert
from .serializers import *
from .tasks import import_ad


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all().order_by('-posted_at')
    serializer_class = AdSerializer
    filter_fields = ['make', 'model', 'year', 'post_url']
    search_fields = ['make__name', 'model__name', 'year', 'title_status', 'post_url']

    @list_route(methods=['post'])
    def import_ad(self, request):
        post_url, post_url_fields = None, ('post_url', 'url')
        for field in post_url_fields:
            post_url = request.data.get(field)
            if post_url:
                break
        if not post_url:
            content = {'message': 'post_url or url is missing'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        if not request.auth or not request.auth.key:
            content = {'message': 'token authorization is required!'}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        # trigger import_ad task
        import_ad.delay(post_url, request.auth.key)
        content = {'message': 'add one task to add this post'}
        return Response(content, status=status.HTTP_200_OK)


class MakeViewSet(viewsets.ModelViewSet):
    queryset = Make.objects.all().order_by('name')
    serializer_class = MakeSerializer
    filter_fields = ['name']
    search_fields = ['name']

    @list_route()
    def with_ads(self, request):
        with_ads = Make.objects.annotate(ads_count=Count('ad')).filter(ads_count__gt=0)
        page = self.paginate_queryset(with_ads)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(with_ads, many=True)
        return Response(serializer.data)


class CarModelViewSet(viewsets.ModelViewSet):
    queryset = CarModel.objects.all().order_by('name')
    serializer_class = CarModelSerializer
    filter_fields = ['name', 'model']
    search_fields = ['name', 'model__name']


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all().order_by('-created_at')
    serializer_class = AlertSerializer

    def create(self, request, pk=None):
        alert = self.get_object()
        if request.user and request.user.is_authenticated:
            alert.owner = request.user
        return super(AlertViewSet, self).create(request, pk=pk)

    def get_queryset(self):
        """
        This view should return a list of all the alerts
        for the currently authenticated user.
        """
        user = self.request.user
        return Alert.objects.filter(owner=user).order_by('-created_at')
