from django.dispatch import receiver
from django.db.models.signals import pre_save
from .models import Order, Transaction

@receiver(pre_save, sender=Transaction)
def sync_paid(sender, instance, **kwargs):
    if instance.status == Transaction.TransactionStatusChoice.PAID and instance.order.status == Order.OrderStatus.SUBMITTED:
        instance.order.status = Order.OrderStatus.CONFIRMED
        instance.order.save()


@receiver(pre_save, sender=Order)
def status_notification(sender, instance, **kwargs):
    if not instance.pk:
        return
    old_status = Order.objects.get(pk=instance.pk).status
    if instance.status == Order.OrderStatus.CONFIRMED and old_status == Order.OrderStatus.SUBMITTED:
        transaction = instance.transactions.first()
        if transaction.status != Transaction.TransactionStatusChoice.PAID:
            transaction.status = Transaction.TransactionStatusChoice.PAID
            transaction.save()
        print('SMS Notification - PAID ORDER')

    if instance.status == Order.OrderStatus.DELIVERING and old_status != instance.status and instance.postal_id:
        print(f'SMS Notification - DELIVERING ORDER - {instance.postal_id}')

    if instance.status == Order.OrderStatus.DONE and old_status != Order.OrderStatus.DONE:
        print('SMS Notification - DONE ORDER')

    if instance.status == Order.OrderStatus.ABORTED and old_status != Order.OrderStatus.ABORTED:
        print('SMS Notification - ABORTED ORDER')