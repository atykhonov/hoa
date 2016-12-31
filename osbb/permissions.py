# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import permissions

from osbb.models import HousingCooperative


class IsManager(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff

    def has_object_permission(self, request, view, entity):
        cooperative = None
        if isinstance(entity, HousingCooperative):
            cooperative = entity
        else:
            cooperative = entity.get_cooperative()
        return request.user.is_manager_of(cooperative)


class NoPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, cooperative):
        return False
