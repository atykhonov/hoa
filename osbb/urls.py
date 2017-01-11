# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import urls, routers
from rest_framework_jwt.views import obtain_jwt_token

from osbb.views.home import HomePageView
from osbb.views.login import LoginPageView, LogoutPageView
from osbb.views.api import (
    AccountViewSet,
    ApartmentViewSet,
    ApartmentMeterIndicatorViewSet,
    HouseViewSet,
    HousingCooperativeViewSet,
    MeterViewSet,
    ServiceViewSet,
    UnitAPIView,
)


router = routers.DefaultRouter()
router.register(r'accounts', AccountViewSet, 'account')
router.register(r'cooperatives', HousingCooperativeViewSet, 'cooperative')
router.register(r'houses', HouseViewSet, 'house')
router.register(r'apartments', ApartmentViewSet, 'apartment')
router.register(r'services', ServiceViewSet, 'service')
router.register(r'meters', MeterViewSet, 'meter')
router.register(
    r'meter-indicators', ApartmentMeterIndicatorViewSet, 'meter-indicator')
# router.register(r'units', UnitAPIView.as_view(), 'unit')


urlpatterns = [
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^accounts/login/', LoginPageView.as_view(), name='login'),
    url(r'^logout/', LogoutPageView.as_view(), name='logout'),
    url(r'^api-auth/', include(urls, namespace='rest_framework')),
    url(r'^api-token-auth/', obtain_jwt_token, name='api-token-auth'),
    url(r'^api/v1/units/', UnitAPIView.as_view()),
    url(r'^api/v1/', include(router.urls)),
]
