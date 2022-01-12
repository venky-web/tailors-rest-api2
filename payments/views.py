from django.shortcuts import get_object_or_404

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from payments.models import Payment
from payments.serializers import PaymentSerializer
from helpers import functions as f


class PaymentListCreateView(ListCreateAPIView):
    """Creates a payment obj or returns list of payments"""
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """returns payment queryset"""
        return Payment.objects.filter(is_deleted=False).order_by("-updated_on")

    def list(self, request, *args, **kwargs):
        """returns list of payments"""
        customer_id = request.query_params.get("customer_id")
        if customer_id:
            payments = self.get_queryset().filter(user_id=customer_id)
        else:
            payments = self.get_queryset()

        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """creates a new payment in db"""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(
            request_user=request.user,
            created_on=f.get_current_time(),
            updated_on=f.get_current_time()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentDetailView(RetrieveUpdateDestroyAPIView):
    """retrieves, updates and destroys a payment obj"""
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """returns payment queryset"""
        return Payment.objects.filter(is_deleted=False).order_by("-updated_on")

    def retrieve(self, request, *args, **kwargs):
        """returns a payment obj based on id"""
        payment_id = kwargs["payment_id"]
        if not payment_id:
            error = {
                "message": "Payment id is missing or invalid"
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(self.get_queryset(), pk=payment_id, is_deleted=False)
        serialized_data = self.get_serializer(payment).data
        return Response(serialized_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """updates a payment obj based on id"""
        payment_id = kwargs["payment_id"]
        if not payment_id:
            error = {
                "message": "Payment id is missing or invalid"
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(self.get_queryset(), pk=payment_id, is_deleted=False)
        serializer = self.get_serializer(payment, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(
            request_user=request.user,
            updated_on=f.get_current_time()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """destroys a payment obj"""
        payment_id = kwargs["payment_id"]
        if not payment_id:
            error = {
                "message": "Payment id is missing or invalid"
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(self.get_queryset(), pk=payment_id, is_deleted=False)
        modified_data = self.get_serializer(payment).data
        modified_data["is_deleted"] = True
        serializer = self.get_serializer(payment, data=modified_data, partial=True)
        serializer.is_valid()
        serializer.save(
            request_user=request.user,
            updated_on=f.get_current_time()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
