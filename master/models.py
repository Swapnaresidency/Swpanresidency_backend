from django.db import models
from django.core.validators import RegexValidator

class RoomType(models.Model):

    AC_CHOICES = [
        ("AC", "AC"),
        ("NON_AC", "Non AC"),
    ]

    category = models.CharField(max_length=50)

    is_ac = models.CharField(
        max_length=10,
        choices=AC_CHOICES
    )

    rent = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category} - {self.get_is_ac_display()}"
class Room(models.Model):
    ROOM_STATUS = [
        ("AVAILABLE", "Available"),
        ("OCCUPIED", "Occupied"),
        ("MAINTENANCE", "Maintenance"),
    ]

    room_no = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=ROOM_STATUS, default="AVAILABLE")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.room_no} - {self.room_type}"

    # --- New Status Helper Methods ---
    def occupy(self):
        """Marks the room as occupied."""
        self.status = "OCCUPIED"
        self.save(update_fields=["status"])

    def make_available(self):
        """Marks the room as available."""
        self.status = "AVAILABLE"
        self.save(update_fields=["status"])
    

class Customer(models.Model):

    ID_TYPE_CHOICES = [
        ("AADHAR", "Aadhar Card"),
        ("PAN", "PAN Card"),
        ("PASSPORT", "Passport"),
        ("DRIVING_LICENSE", "Driving License"),
        ("VOTER_ID", "Voter ID"),
    ]

    customer_code = models.CharField(
        max_length=20,
        unique=True
    )

    customer_name = models.CharField(
        max_length=100
    )
    mobile_regex = RegexValidator(
    regex=r'^[6-9]\d{9}$', 
    message="Mobile number must be a valid 10-digit Indian number starting with 6, 7, 8, or 9."
    )
    mobile_no = models.CharField(
    validators=[mobile_regex],
    max_length=10,
    unique=True
    )
    email = models.EmailField(
        blank=True,
        null=True,
        unique=True
    )

    address = models.TextField()

    id_type = models.CharField(
        max_length=20,
        choices=ID_TYPE_CHOICES
    )

    # Upload file/image
    id_proof = models.FileField(
    upload_to='customer_id_proofs/',
    blank=True,
    null=True
)

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer_code} - {self.customer_name}"