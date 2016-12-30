# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import permissions


class CooperativePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff

    def has_object_permission(self, request, view, cooperative):
        user = request.user
        user_cooperative = request.user.cooperative
        if user_cooperative:
            return user_cooperative.id == cooperative.id and user.is_staff
        return False


class NoPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, cooperative):
        return False
