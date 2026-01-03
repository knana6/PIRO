from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    GENDER_CHOICES = [
        ('Male', '남자'),
        ('Female', '여자'),
    ]

    JOB_CHOICES = [
        ('Student', '학생'),
        ('Worker', '직장인'),
        ('Other', '기타'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20, blank=True)
    birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    job = models.CharField(max_length=10, choices=JOB_CHOICES, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(default='default.jpg',upload_to='profile_pics')

    def __str__(self):
        return f"{self.user.username} Profile"