from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from user_profile.models import Department
# Create your models here.

LEAVE_CHOICE = (

    ('casual', 'casual'),
    ('vacation', 'vacation'),
    ('commuted', 'commuted'),
    ('special casual', 'special casual'),
    ('restricted', 'restricted'),
    ('station leave', 'station leave'),

)

PROCESSING_BY_CHOICES = (

    ('hod', 'Head Of Department'),
    ('director', 'Director')

)

APPLICATION_STATUSES = (

    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
    ('processing', 'Being Processed')

)

class Leave(models.Model):
    applicant = models.ForeignKey(User, related_name='applied_for', on_delete=models.CASCADE)
    replacing_user = models.ForeignKey(User, related_name='replaced_for', on_delete=models.CASCADE)
    type_of_leave = models.CharField(max_length=20, choices=LEAVE_CHOICE)
    applied_time = models.DateTimeField(auto_now=True)
    start_date = models.DateField()
    end_date = models.DateField()
    purpose = models.CharField(max_length=500, blank=False)
    leave_address = models.CharField(max_length=100, blank=True)
    processing_status = models.CharField(max_length=20, default='hod', choices=PROCESSING_BY_CHOICES)
    application_status = models.CharField(max_length=20, default='processing', choices=APPLICATION_STATUSES)


class RemainingLeaves(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    casual = models.IntegerField(default=30)
    vacation = models.IntegerField(default=60)
    commuted = models.IntegerField(default=10)
    special_casual = models.IntegerField(default=15)
    restricted = models.IntegerField(default=2)

    def __str__(self):
        return '{} has {} casual leaves left'.format(self.user.username, self.casual)

@receiver(post_save, sender=User)
def create_remaining_leaves(sender, instance, created, **kwargs):
    if created and instance.extrainfo.user_type != 'student':
        RemainingLeaves.objects.create(user=instance)
