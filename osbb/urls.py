# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import urls, routers

from osbb.views.home import HomePageView
from osbb.views.login import LoginPageView, LogoutPageView
from osbb.views.cooperative import HousingCooperativeViewSet


router = routers.DefaultRouter()
router.register(r'cooperatives', HousingCooperativeViewSet, 'cooperative')


urlpatterns = [
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^accounts/login/', LoginPageView.as_view(), name='login'),
    url(r'^logout/', LogoutPageView.as_view(), name='logout'),
    url(r'^api-auth/', include(urls, namespace='rest_framework')),
    url(r'^api/v1/', include(router.urls)),
]
