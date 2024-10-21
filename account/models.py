from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# class UserProfile(models.Model):
#     GENDER_CHOICES = [
#         ('male', 'Male'),
#         ('female', 'Female'),
#         ('other', 'Other'),
#     ]

#     user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE)
#     date_of_birth = models.DateField(null=True, blank=True)
#     gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)

#     def __str__(self):
#         return self.user.first_name
class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.user.first_name

class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        expiration_time = timezone.now() - timezone.timedelta(hours=24)
        return self.created_at < expiration_time

    def regenerate_token(self):
        self.token = uuid.uuid4()
        self.created_at = timezone.now()
        self.save()




