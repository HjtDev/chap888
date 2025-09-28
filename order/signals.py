from django.dispatch import receiver
from django.db.models.signals import pre_save
from .models import Order, Transaction
from sms.sms import sms


@receiver(pre_save, sender=Transaction)
def sync_paid(sender, instance, **kwargs):
    if (
            instance.status == Transaction.TransactionStatusChoice.PAID
            and instance.order.status == Order.OrderStatus.SUBMITTED
    ):
        instance.order.status = Order.OrderStatus.CONFIRMED
        instance.order.save()


@receiver(pre_save, sender=Order)
def status_notification(sender, instance: Order, **kwargs):
    if not instance.pk:
        sms.notify_admin(instance.user.first_name, instance.user.phone, instance.order_id)
        return
    old_status = Order.objects.get(pk=instance.pk).status
    if (
            instance.status == Order.OrderStatus.CONFIRMED
            and old_status == Order.OrderStatus.SUBMITTED
    ):
        transaction = instance.transactions.first()
        if transaction.status != Transaction.TransactionStatusChoice.PAID:
            transaction.status = Transaction.TransactionStatusChoice.PAID
            transaction.save()
        # print("SMS Notification - PAID ORDER")
        sms.order_confirmed(instance.user.phone, instance.user.first_name, instance.order_id)
    
    if (
            instance.status == Order.OrderStatus.READY_TO_DELIVER
            and old_status != instance.status
    ):
        # print(f"SMS Notification - DELIVERING ORDER - {instance.postal_id}")
        if instance.postal_id:
            sms.order_shipped(instance.user.phone, instance.user.first_name, instance.order_id)
        else:
            sms.order_ready(instance.user.phone, instance.user.first_name, instance.order_id)
    
    if (
            instance.status == Order.OrderStatus.DONE
            and old_status != Order.OrderStatus.DONE
    ):
        # print("SMS Notification - DONE ORDER")
        sms.order_completed(instance.user.phone, instance.user.first_name, instance.order_id)
    
    if (
            instance.status == Order.OrderStatus.ABORTED
            and old_status != Order.OrderStatus.ABORTED
    ):
        # print("SMS Notification - ABORTED ORDER")
        sms.order_canceled(instance.user.phone, instance.user.first_name, instance.order_id)
