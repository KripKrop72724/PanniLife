import stripe
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from BaseModules.models import Customer
from BaseModules.serializer import CustomerSerializer, CheckoutLinkRequestSerializer, CustomerUpdateSerializer, \
    CommentUpdateSerializer, ImageUpdateSerializer, VideoUpdateSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        customer = self.get_object()
        serializer = CustomerUpdateSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def update_comment(self, request, pk=None):
        customer = self.get_object()
        serializer = CommentUpdateSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def update_images(self, request, pk=None):
        customer = self.get_object()
        serializer = ImageUpdateSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def update_videos(self, request, pk=None):
        customer = self.get_object()
        serializer = VideoUpdateSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


stripe.api_key = settings.STRIPE_SECRET_KEY


class CheckoutLinkView(APIView):
    def post(self, request):
        serializer = CheckoutLinkRequestSerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            success_url = serializer.validated_data['success_url']
            cancel_url = serializer.validated_data['cancel_url']

            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

            try:
                # Create line items for the checkout session
                line_items = []

                # Add well prices
                line_items.append({
                    'price': settings.WELL_PRICE,
                    'quantity': customer.number_of_wells
                })

                # Add tip price if tip_added is true
                if customer.tip_added:
                    line_items.append({
                        'price': settings.TIP_PRICE,
                        'quantity': 1
                    })

                # Create a checkout session
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    customer=customer.donor_stripe_id,
                    line_items=line_items,
                    mode='payment',
                    success_url=success_url,
                    cancel_url=cancel_url
                )

                return Response({"checkout_url": checkout_session.url}, status=status.HTTP_200_OK)
            except stripe.error.StripeError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerViewSetProtected(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
