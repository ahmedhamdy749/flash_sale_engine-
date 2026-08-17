from django.urls import path
from .views import FlashSaleListView, PurchaseFlashSaleView

urlpatterns = [
    path('flash-sales/', FlashSaleListView.as_view(), name='flash-sale-list'),
    path('purchase/', PurchaseFlashSaleView.as_view(), name='purchase-flash-sale'),
]