from rest_framework import permissions


class PermissionItem:
    codename = None
    app_label = None

    def __init__(self, app_label, codename):
        self.app_label = app_label
        self.codename = codename

    @property
    def perm(self):
        return "{}.{}".format(self.app_label, self.codename)

    def __str__(self):
        return self.perm
