from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import generics, status, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from account.serializers import UserSerializer, BusinessSerializer, UserProfileSerializer, \
    UserProfileReadOnlySerializer
from helpers import functions as helpers
from account import models, permissions
from account import custom_functions as c_func


class UserCreateView(generics.CreateAPIView):
    """view to create a new user"""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """creates a new user in db"""
        c_func.check_for_username_password(request)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        now = helpers.get_current_time()
        serializer.save(
            created_on=now,
            updated_on=now,
        )
        user = serializer.data
        business_id = request.query_params.get("bid", None)
        if business_id is not None:
            c_func.add_user_business_relation(business_id, user["id"], comments="Auto approved", status="Approved")
        response = Response()
        response.data = {
            "user": user,
        }
        return c_func.add_tokens(response, user)


class BusinessUserCreateView(generics.CreateAPIView):
    """view to create a new user"""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """creates a new user in db"""
        c_func.check_for_username_password(request)
        business_data = request.data.get("business", None)
        if business_data is None:
            error = {
                "message": "Business information is missing"
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        now = helpers.get_current_time()
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
        business_instance = c_func.update_business_staff_count(business.id)
        user = serializer.data
        response_data = {
            "user": user
        }
        response_data["user"]["business"] = BusinessSerializer(business_instance).data
        response = Response(data=response_data)
        return c_func.add_tokens(response, user)


class BusinessStaffUserView(generics.ListCreateAPIView):
    """creates a user or returns a list"""
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, permissions.IsOwner,
                          permissions.MaxStaffCount)

    def get_queryset(self):
        """returns queryset of users"""
        if self.request.user.is_superuser:
            return get_user_model().objects.all()

        return get_user_model().objects.filter(Q(business=self.request.user.business.id),
                                               ~Q(id=self.request.user.id))

    def list(self, request, *args, **kwargs):
        """returns list of users with matching business id"""
        queryset = self.get_queryset()
        response_data = c_func.get_users(queryset)
        return Response(response_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """creates a new user in db"""
        business = None
        detail = {
            "message": "Business details are missing"
        }
        if request.user.is_superuser:
            business_id = request.data["business"]
            if business_id is None:
                return Response(detail, status=status.HTTP_400_BAD_REQUEST)

            business = models.Business.objects.filter(id=business_id).first()
        elif request.user.business:
            business = request.user.business

        if business is None:
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)

        c_func.check_for_username_password(request)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        now = helpers.get_current_time()
        serializer.save(
            created_on=now,
            updated_on=now,
            request_user=request.user,
            business=business,
            user_role="business_staff"
        )
        c_func.update_business_staff_count(business.id)
        response_data = c_func.get_users(self.get_queryset())
        return Response(response_data, status=status.HTTP_200_OK)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """user detail view to retrieve, update and destroy"""
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, permissions.IsUpdateProfile)

    def get_queryset(self):
        """returns queryset of active users"""
        return get_user_model().objects.filter(is_active=True)

    def retrieve(self, request, *args, **kwargs):
        """returns a user obj with user id"""
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=kwargs["id"])
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(user)
        response_data = c_func.get_user_profile_and_business_data(serializer.data)
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
            updated_on=helpers.get_current_time()
        )
        response_data = c_func.get_user_profile_and_business_data(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """deactivates a user"""
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=kwargs["id"])
        self.check_object_permissions(request, user)
        user.is_active = False
        user.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class BusinessDetailView(generics.RetrieveUpdateDestroyAPIView):
    """view to retrieve, update and destroy business obj"""
    queryset = models.Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = (IsAuthenticated, permissions.IsBusinessAdminOrSuperuser)

    def retrieve(self, request, *args, **kwargs):
        """returns business obj with valid id"""
        queryset = self.get_queryset()
        business = get_object_or_404(queryset, pk=kwargs["id"])
        self.check_object_permissions(request, business)
        serialized_data = self.get_serializer(business).data
        return Response(serialized_data)

    def update(self, request, *args, **kwargs):
        """updates a business obj with valid id"""
        queryset = models.Business.objects.all()
        business = get_object_or_404(queryset, pk=kwargs["id"])
        self.check_object_permissions(request, business)
        serializer = self.get_serializer(business, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            updated_on=helpers.get_current_time(),
            request_user=request.user
        )
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """deletes a business obj with valid id"""
        queryset = self.get_queryset()
        business = get_object_or_404(queryset, pk=kwargs["id"])
        self.check_object_permissions(request, business)
        business.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """retrieves and updates user profile data"""
    serializer_class = UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    permission_classes = (IsAuthenticated, permissions.IsUpdateProfile,)

    def retrieve(self, request, *args, **kwargs):
        """returns user profile data with matching user id"""
        user = get_user_model().objects.filter(id=kwargs["id"]).first()
        if not user:
            error = {
                "message": "User not found"
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        if user.id == request.user.id or request.user.is_superuser or \
            (request.user.user_role == "business_admin" and
            request.user.business and user.business and
            request.user.business.id == user.business.id):
            response_data = c_func.get_user_profile_and_business_data(UserSerializer(user).data)
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            error = {
                "message": "Unauthorized request"
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """updates a user profile"""
        user = get_user_model().objects.filter(id=kwargs["id"]).first()
        if not user:
            error = {
                "message": "User not found"
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        self.check_object_permissions(request, user)
        queryset = self.get_queryset()
        user_profile = queryset.filter(user=kwargs["id"]).first()
        c_func.save_user_profile(request, user, user_profile)
        response_data =  c_func.get_user_profile_and_business_data(UserSerializer(user).data)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated, permissions.IsBusinessAdminOrStaff])
def customers_list(request):
    """view to return list of customers tagged to business"""

    user_business_relations = models.UserBusinessRelation.objects.filter(business_id=request.user.business.id)
    users = []
    for relation in user_business_relations:
        user = get_user_model().objects.filter(id=relation.user_id).first()
        if user:
            serialized_data = UserSerializer(user).data
            profile = models.UserProfile.objects.filter(user=relation.user_id).first()
            if profile:
                serialized_data["profile"] = UserProfileReadOnlySerializer(profile).data
            users.append(serialized_data)
    response = Response(data=users, status=status.HTTP_200_OK)
    return response
