from celery import shared_task
from django.db import transaction
from .models import Order, FlashSale

@shared_task
def create_order_async(user_id, flash_sale_id, idempotency_key):
    try:
        with transaction.atomic():
            flash_sale = FlashSale.objects.select_for_update().get(id=flash_sale_id)
            
            if flash_sale.total_stock > 0:
                flash_sale.total_stock -= 1
                flash_sale.save()

                Order.objects.create(
                    user_id=user_id,
                    flash_sale=flash_sale,
                    status='PENDING',
                    idempotency_key=idempotency_key
                )
                return True
            else:
                # Stock exhausted in DB
                return False
    except Exception as e:
        # Prevent duplicated insertion if idempotency key fails
        return False