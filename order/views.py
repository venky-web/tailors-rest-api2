from django.db.models import Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from orders.models import Order, OrderItem
from orders import serializers
from helpers import functions as f


class OrderListCreateView(ListCreateAPIView):
    """ViewSet for orders"""
    serializer_class = serializers.OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """returns order list based on user type"""
        user = self.request.user
        orders = Order.objects.filter(Q(created_by=user.id) | Q(updated_by=user.id), Q(is_deleted="N"))
        return orders

    def list(self, request, *args, **kwargs):
        """returns a list of orders"""
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Creates a new order in the DB"""
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = self.request.user
        now = f.get_current_time()
        serializer.save(request_user=user, created_on=now, updated_on=now)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieves, updates and deletes order"""
    serializer_class = serializers.OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """returns an order queryset for current user"""
        user = self.request.user
        orders = Order.objects.filter(created_by=user.id, is_deleted="N")
        return orders

    def retrieve(self, request, *args, **kwargs):
        """returns an order"""
        order = self.get_queryset().filter(pk=kwargs["id"]).first()
        if not order:
            error = {
                "message": f"Order with id ({kwargs['id']}) cannot be found"
            }
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """updates an order in the db"""
        user = self.request.user
        order = self.get_queryset().filter(pk=kwargs["id"]).first()
        if not order:
            error = {
                "message": f"Order with id ({kwargs['id']}) cannot be found"
            }
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(order, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(request_user=user, updated_on=f.get_current_time())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """sets is_deleted flag to Y for order instance"""
        order = self.get_queryset().filter(pk=kwargs["id"]).first()
        if not order:
            error = {
                "message": f"Order with id ({kwargs['id']}) cannot be found"
            }
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        user = self.request.user
        modified_product = self.get_serializer(order).data
        modified_product["is_deleted"] = "Y"
        serializer = self.get_serializer(order, data=modified_product)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(request_user=user, updated_on=f.get_current_time())
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class OrderItemListCreateView(ListCreateAPIView):
    """List and create view for order item"""
    serializer_class = serializers.OrderItemSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """returns queryset for order items"""
        order_id = self.kwargs["order_id"]
        order_items = OrderItem.objects.filter(order_id=order_id, is_deleted="N")
        return order_items

    def list(self, request, *args, **kwargs):
        """returns a list of order items specific to the order"""
        order = Order.objects.filter(pk=kwargs["order_id"], is_deleted="N").first()
        if not order:
            error = {
                "message": f"Order with id ({kwargs['order_id']}) is not found"
            }
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """creates a new order item for the specified order"""
        order = Order.objects.filter(pk=kwargs["order_id"], is_deleted="N").first()
        if not order:
            error = {
                "message": f"Order with id ({kwargs['order_id']}) is not found"
            }
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        user = self.request.user
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        now = f.get_current_time()
        serializer.save(request_user=user, order=order, created_on=now, updated_on=now)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderItemViewSet(ModelViewSet):
    """viewSet for order items"""
    queryset = OrderItem.objects.all()
    serializer_class = serializers.OrderItemSerializer
    permission_classes = (IsAuthenticated,)
