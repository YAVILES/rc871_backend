import tablib
from django.db.models.query_utils import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action, authentication_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from tablib import Dataset
from django_filters import rest_framework as filters
from rc871_backend.utils.functions import format_headers_import
from .admin import UserResource, RoleResource
from .models import User, Workflow, Role
from .serializers import UserDefaultSerializer, CustomTokenObtainPairSerializer, RoleDefaultSerializer, \
    UserCreateSerializer, WorkflowDefaultSerializer, UserCreateClientSerializer


class UserFilter(filters.FilterSet):

    class Meta:
        model = User
        fields = ['username', 'is_active', 'name', 'email', 'email_alternative', 'code', 'is_staff']


class UserViewSet(ModelViewSet):
    queryset = User.objects.all() #filter(Q(is_staff=True) | Q(is_superuser=True))
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = UserFilter
    serializer_class = UserDefaultSerializer
    search_fields = ['username', 'name', 'email', 'email_alternative', 'code', 'is_staff']
    permission_classes = (AllowAny,)

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_queryset(self):
        queryset = self.queryset

        # Superuser can see everything
        if self.request.user.is_superuser and self.action == 'retrieve':
            return queryset

        # Staff can see everything except superusers
        if self.request.user.is_staff:
            return queryset.filter(is_superuser=False)

        # Rest of users can see themselves
        # if self.action == 'retrieve':
        #    return queryset.filter(pk=self.request.user.pk)

        return queryset
        # Can't list users
        # return queryset.none()

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return UserCreateSerializer
        return UserDefaultSerializer

    @authentication_classes([])
    @action(methods=['POST', ], detail=False)
    def create_client(self, request, *args, **kwargs):
        serializer = UserCreateClientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['GET', ], detail=False)
    def current(self, request):
        return Response(UserDefaultSerializer(request.user).data)

    @action(methods=['GET'], detail=False)
    def export(self, request):
        dataset = UserResource().export()
        return Response(dataset.csv, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = UserResource()
            errors = []
            invalids = []
            if request.FILES:
                file = request.FILES['file']
                data_set = Dataset()
                data_set.load(file.read())
                data_set.headers = format_headers_import(data_set.headers)
                result = resource.import_data(data_set, dry_run=True)  # Test the data import
            else:
                headers = request.data['headers']
                data_set = tablib.Dataset(headers=headers)
                for d in request.data['data']:
                    data_set.append(d)
                result = resource.import_data(data_set, dry_run=True)

            if result.has_errors() or len(result.invalid_rows) > 0:
                for row in result.invalid_rows:
                    invalids.append(
                        {
                            "row": row.number + 1,
                            "error": row.error,
                            "error_dict": row.error_dict,
                            "values": row.values
                        }
                    )

                for row in result.row_errors():
                    err = row[1]
                    errors.append(
                        {
                            "errors": [e.error.__str__() for e in err],
                            "values": err[0].row,
                            "row": row[0]
                        }
                    )

                return Response({
                    "rows_error": errors,
                    "invalid_rows": invalids,
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                result = resource.import_data(data_set, dry_run=False)  # Actually import now
                return Response({
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=False)
    def field_options(self, request):
        field = self.request.query_params.get('field', None)
        fields = self.request.query_params.getlist('fields', None)
        if fields:
            try:
                data = {}
                for field in fields:
                    data[field] = []
                    for c in User._meta.get_field(field).choices:
                        data[field].append({
                            "value": c[0],
                            "description": c[1]
                        })
                return Response(data, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response(e, status=status.HTTP_400_BAD_REQUEST)
        elif field:
            try:
                choices = []
                for c in User._meta.get_field(field).choices:
                    choices.append({
                        "value": c[0],
                        "description": c[1]
                    })
                return Response(choices, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response(e, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "the field parameter is mandatory"}, status=status.HTTP_400_BAD_REQUEST)


class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleDefaultSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name']

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(methods=['GET'], detail=False)
    def export(self, request):
        dataset = RoleResource().export()
        return Response(dataset.csv, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = RoleResource()
            errors = []
            invalids = []
            if request.FILES:
                file = request.FILES['file']
                data_set = Dataset()
                data_set.load(file.read())
                data_set.headers = format_headers_import(data_set.headers)
                result = resource.import_data(data_set, dry_run=True)  # Test the data import
            else:
                headers = request.data['headers']
                data_set = tablib.Dataset(headers=headers)
                for d in request.data['data']:
                    data_set.append(d)
                result = resource.import_data(data_set, dry_run=True)

            if result.has_errors() or len(result.invalid_rows) > 0:
                for row in result.invalid_rows:
                    invalids.append(
                        {
                            "row": row.number + 1,
                            "error": row.error,
                            "error_dict": row.error_dict,
                            "values": row.values
                        }
                    )

                for row in result.row_errors():
                    err = row[1]
                    errors.append(
                        {
                            "errors": [e.error.__str__() for e in err],
                            "values": err[0].row,
                            "row": row[0]
                        }
                    )

                return Response({
                    "rows_error": errors,
                    "invalid_rows": invalids,
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                result = resource.import_data(data_set, dry_run=False)  # Actually import now
                return Response({
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class WorkflowViewSet(ReadOnlyModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowDefaultSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['title', 'url']

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
