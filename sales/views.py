from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import FlashSale
from .serializers import FlashSaleSerializer, PurchaseRequestSerializer
from .services import reserve_flash_sale_item
from .tasks import create_order_async

class FlashSaleListView(generics.ListAPIView):
    queryset = FlashSale.objects.filter(is_active=True)
    serializer_class = FlashSaleSerializer

class PurchaseFlashSaleView(APIView):
    def post(self, request):
        serializer = PurchaseRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        flash_sale_id = serializer.validated_data['flash_sale_id']
        idempotency_key = serializer.validated_data['idempotency_key']
        user_id = request.user.id if request.user.is_authenticated else 1  # Fallback for dev

        # 1. Atomic decrement in Redis via Lua Script
        stock_reserved = reserve_flash_sale_item(flash_sale_id)

        if not stock_reserved:
            return Response(
                {"detail": "Out of stock or sale ended!"},
                status=status.HTTP_410_GONE
            )

        # 2. Enqueue DB write job into Celery
        create_order_async.delay(user_id, flash_sale_id, idempotency_key)

        return Response(
            {"detail": "Order accepted! Processing in background."},
            status=status.HTTP_202_ACCEPTED
        )