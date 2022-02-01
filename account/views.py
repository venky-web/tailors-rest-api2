from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from account.serializers import UserSerializer, BusinessSerializer
from helpers import functions as f
from account import models, permissions
from account.custom_functions import update_business_staff_count, \
    check_for_username_password
from core.authentication import generate_access_token, generate_refresh_token


class UserCreateView(generics.CreateAPIView):
    """view to create a new user"""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """creates a new user in db"""
        check_for_username_password(request)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        now = f.get_current_time()
        serializer.save(
            created_on=now,
            updated_on=now,
        )
        user = serializer.data
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
        response = Response()
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        response.data = {
            "access_token": access_token,
            "user": user,
        }
        return response


class BusinessUserCreateView(generics.CreateAPIView):
    """view to create a new user"""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """creates a new user in db"""
        check_for_username_password(request)
        now = f.get_current_time()
        business_data = request.data.get("business", None)
        if business_data is None:
            error = {
                "message": "Business information is missing"
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        # business data serialization
        business_serializer = BusinessSerializer(data=business_data)
        business_serializer.is_valid(raise_exception=True)
        # user data serialization
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        business_serializer.save(created_on=now, updated_on=now)
        business = models.Business.objects.filter(id=business_serializer.data["id"]).first()
        serializer.save(
            created_on=now,
            updated_on=now,
            business=business,
            user_role="business_admin"
        )
        business_instance = update_business_staff_count(business.id)
        response = Response()
        user = serializer.data
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        response.data = {
            "access_token": access_token,
            "user": user,
            "business": BusinessSerializer(business_instance).data,
        }
        return response


class UserListView(generics.ListAPIView):
    """creates a user or returns a list"""
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdminUser, permissions.IsOwner)

    def get_queryset(self):
        """returns queryset of users"""
        users = get_user_model().objects.filter(business=self.request.user.business)
        return users


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """user detail view to retrieve, update and destroy"""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, permissions.IsOwner)

    def retrieve(self, request, *args, **kwargs):
        """returns a user obj with user id"""
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=kwargs["id"])
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(user)
        response_data = serializer.data
        if user.business:
            business = models.Business.objects.filter(pk=user.business).first()
            response_data["business"] = BusinessSerializer(business).data
        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """updates a user obj"""
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=kwargs["id"])
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            request_user=request.user,
            updated_on=f.get_current_time()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """deactivates a user"""
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=kwargs["id"])
        self.check_object_permissions(request, user)
        modified_user = self.get_serializer(user).data
        modified_user["is_active"] = False
        serializer = self.get_serializer(user, data=modified_user, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            request_user=request.user,
            updated_on=f.get_current_time()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class StaffUserView(APIView):
    """View to do CRUD operations for staff users"""
    permission_classes = (IsAuthenticated, permissions.IsOwner)

    def get(self, request):
        """returns a staff user"""
        staff_users = get_user_model().objects.filter(business=request.user.business).first()
        response_data = UserSerializer(staff_users, many=True)
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):
        """creates a new staff user"""
        pass

    # def get_queryset(self):
    #     """returns user queryset for staff users"""
    #     return get_user_model().objects.filter(user_role="business_staff")
    #
    # def list(self, request, *args, **kwargs):
    #     """returns list of staff users"""
    #     queryset = self.get_queryset().filter(business=request.user.business)
    #     staff_users = UserSerializer(queryset, many=True).data
    #     return Response(staff_users, status=status.HTTP_200_OK)
    #
    # def create(self, request, *args, **kwargs):
    #     """creates a new staff user"""
    #     serializer = self.serializer_class(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     now = f.get_current_time()
    #     serializer.save(
    #         created_on=now,
    #         updated_on=now,
    #         business=request.user.business,
    #         user_role="business_staff"
    #     )
    #     return Response(serializer.data, status=status.HTTP_200_OK)
