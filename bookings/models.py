from django.db import models
from master.models import Customer, Room

class Booking(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    booking_date = models.DateField(auto_now_add=True)
    checkin_date = models.DateField()
    checkout_date = models.DateField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )

    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.customer} - Room {self.room}"