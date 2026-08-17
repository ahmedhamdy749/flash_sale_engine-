from rest_framework import serializers
from .models import Product, FlashSale, Order

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class FlashSaleSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = FlashSale
        fields = '__all__'

class PurchaseRequestSerializer(serializers.Serializer):
    flash_sale_id = serializers.IntegerField()
    idempotency_key = serializers.CharField(max_length=255)