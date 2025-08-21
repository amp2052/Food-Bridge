from django.db import models 
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin
from django.conf import settings
from django.utils import timezone

# Create your models here.
ROLE_CHOICES=[
  ('donor', 'Donor'),
  ('ngo', 'NGO'),
  ('admin', 'Admin'),
]

class CustomUserManager(BaseUserManager):
    def create_user(self, email, role, password=None, first_name='', last_name=''):
        if not email:
            raise ValueError('User must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            role=role,
            first_name=first_name,
            last_name=last_name,
            
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, role='admin', password=None, first_name='Admin', last_name='User', **extra_fields):
        user = self.create_user(
            email=email,
            role=role,
            password=password,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

  
class CustomUser(AbstractBaseUser,PermissionsMixin):
  email=models.EmailField(unique=True)
  role=models.CharField(max_length=10,choices=ROLE_CHOICES)
  is_active=models.BooleanField(default=True)
  is_staff=models.BooleanField(default=False)

  first_name = models.CharField(max_length=30, blank=True)
  last_name = models.CharField(max_length=30, blank=True)

  date_joined = models.DateTimeField(default=timezone.now) 

  objects=CustomUserManager()

  USERNAME_FIELD='email'
  REQUIRED_FIELDS=['role']

  def __str__(self):
        return f"{self.email} ({self.role})"


class Campaign(models.Model):
    ngo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ngo'},
        related_name='campaigns'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} by {self.ngo.username}"

    @property
    def total_donated(self):
        return self.donations.aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def progress_percentage(self):
        if self.goal_amount > 0:
            return min((self.total_donated / self.goal_amount) * 100, 100)
        return 0

class Donation(models.Model):
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'donor'},
        related_name='donations'
    )
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='donations'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.CharField(max_length=255, blank=True)
    donated_at = models.DateTimeField(auto_now_add=True)
    anonymous = models.BooleanField(default=False)

    def __str__(self):
        return f"₹{self.amount} by {'Anonymous' if self.anonymous else self.donor.username} to {self.campaign.title}"

class FoodDonation(models.Model):
    FOOD_TYPE_CHOICES = [
        ('veg', 'Vegetarian'),
        ('nonveg', 'Non-Vegetarian'),
    ]

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'donor'},
        related_name='food_donations'
    )
    claimed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'ngo'},
        on_delete=models.SET_NULL,
        related_name='claimed_food_donations'
    )
    event_name = models.CharField(max_length=100)
    food_type = models.CharField(max_length=10, choices=FOOD_TYPE_CHOICES)  # changed to choices
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=10, default='kg')  # new field for unit
    pickup_address = models.TextField()
    pickup_deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    ], default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_name} - {self.get_food_type_display()} ({self.status})"



class FoodRequest(models.Model):
    donation = models.ForeignKey(FoodDonation, on_delete=models.CASCADE, related_name='requests')
    ngo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ngo'},
        related_name='food_requests'
    )
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ngo.email} - {self.donation.event_name} ({self.status})"

# -------------------- SystemStats Model (Optional Admin Analytics) --------------------

class SystemStats(models.Model):
    date = models.DateField(auto_now_add=True)
    total_users = models.PositiveIntegerField(default=0)
    total_campaigns = models.PositiveIntegerField(default=0)
    total_donations = models.PositiveIntegerField(default=0)
    total_food_donations = models.PositiveIntegerField(default=0)
    total_food_requests = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"System Stats on {self.date}"


# -------------------- AuditLog Model (Optional Admin Audit Logs) --------------------

class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.created_at}"


# -------------------- Optional UserProfile Model (If needed for extended user info) --------------------

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.name or self.user.email

class NGOProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    organization_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.organization_name
        