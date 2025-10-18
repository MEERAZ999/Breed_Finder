from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        UserProfile.objects.create(user=instance)

class Pet(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available for Adoption'),
        ('PENDING', 'Adoption Pending'),
        ('ADOPTED', 'Adopted'),
    ]
    
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    age_years = models.IntegerField(default=0)
    age_months = models.IntegerField(default=0)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    description = models.TextField()
    image = models.ImageField(upload_to='pets/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='AVAILABLE')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def age_display(self):
        years_text = f"{self.age_years} year{'s' if self.age_years != 1 else ''}" if self.age_years > 0 else ""
        months_text = f"{self.age_months} month{'s' if self.age_months != 1 else ''}" if self.age_months > 0 else ""
        
        if years_text and months_text:
            return f"{years_text}, {months_text}"
        elif years_text:
            return years_text
        elif months_text:
            return months_text
        else:
            return "Unknown"
    
    def __str__(self):
        return f'{self.name} - {self.breed}'
