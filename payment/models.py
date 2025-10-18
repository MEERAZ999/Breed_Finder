from django.db import models
from django.conf import settings
from breed_finder.models import Pet

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('KHALTI', 'Khalti'),
        ('ESEWA', 'eSewa'),
        ('PENDING', 'Pending')
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('INITIATED', 'Initiated'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('EXPIRED', 'Expired'),
        ('REFUNDED', 'Refunded'),
        ('CANCELLED', 'Cancelled')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    transaction_uuid = models.CharField(max_length=36, unique=True, null=True)  # Store UUID as string
    pidx = models.CharField(max_length=100, blank=True, null=True)  # Khalti payment ID
    signature = models.TextField(blank=True, null=True)  # eSewa signature
    payment_url = models.URLField(blank=True, null=True)  # Payment gateway URL
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_as_completed(self):
        self.payment_status = 'COMPLETED'
        self.pet.status = 'ADOPTED'
        self.pet.save()
        self.save()

    def mark_as_failed(self, error_message=None):
        self.payment_status = 'FAILED'
        if error_message:
            self.error_message = error_message
        self.save()

    def __str__(self):
        return f"{self.user.username}'s payment for {self.pet.name} - {self.payment_status}"
