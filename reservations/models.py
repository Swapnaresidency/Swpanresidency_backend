from django.db import models
from master.models import Room, Customer 
from django.db.models import Q
from django.db import transaction

class CheckIn(models.Model):
    PAYMENT_MODES = [
        ("CASH", "Cash"),
        ("CARD", "Card"),
        ("UPI", "UPI"),
        ("NET_BANKING", "Net Banking"),
    ]
    STATUS_CHOICES = [
        ("CHECKED_IN", "Checked In"),
        ("CHECKED_OUT", "Checked Out"),
        ("CANCELLED", "Cancelled"),
    ]
    
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name="checkins"
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="checkins"
    )
    checkin_date = models.DateField()
    checkin_time = models.TimeField()
    base_daily_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    pay_mode = models.CharField(max_length=20, choices=PAYMENT_MODES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="CHECKED_IN")
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.customer.customer_name} - Room {self.room.room_no}"

    def save(self, *args, **kwargs):
        """
        Overrides save to dynamically update the associated room's status.
        Uses an atomic transaction to guarantee data synchronization.
        """
        with transaction.atomic():
            super().save(*args, **kwargs)
            
            # Update the room status depending on the checkin status
            if self.status == "CHECKED_IN":
                self.room.status = "OCCUPIED"
                self.room.save(update_fields=['status'])
            elif self.status in ["CHECKED_OUT", "CANCELLED"]:
                self.room.status = "AVAILABLE"
                self.room.save(update_fields=['status'])


class CheckOut(models.Model):
    PAYMENT_TYPES = [
        ("CASH", "Cash"),
        ("CARD", "Card"),
        ("UPI", "UPI"),
        ("NET_BANKING", "Net Banking"),
    ]
    
    checkin = models.OneToOneField(
        CheckIn,
        on_delete=models.CASCADE,
        related_name="checkout"
    )
    checkout_date = models.DateField()
    checkout_time = models.TimeField()
    total_days = models.PositiveIntegerField()
    balance_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pay_mode = models.CharField(max_length=20, choices=PAYMENT_TYPES) 
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remarks = models.TextField(blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self): 
        return f"Checkout - {self.checkin.customer.customer_name}"

    def save(self, *args, **kwargs):
        """
        Overrides save to ensure the original CheckIn status updates 
        and the linked Room frees up automatically.
        """
        with transaction.atomic():
            super().save(*args, **kwargs)
            
            # Update parent CheckIn entry status
            checkin_instance = self.checkin
            if checkin_instance.status != "CHECKED_OUT":
                checkin_instance.status = "CHECKED_OUT"
                checkin_instance.save(update_fields=['status'])
                
            # Direct backup update to make certain the room gets freed
            room_instance = checkin_instance.room
            if room_instance.status != "AVAILABLE":
                room_instance.status = "AVAILABLE"
                room_instance.save(update_fields=['status'])