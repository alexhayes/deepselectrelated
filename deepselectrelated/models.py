from django.db import models
from django.contrib.auth import get_user_model

class Task(models.Model):
    title = models.CharField(max_length=60)
    creator = models.ForeignKey(get_user_model(), related_name='created_tasks')
    owner = models.ForeignKey(get_user_model(), related_name='owned_tasks')

    def __unicode__(self):
        return '%s' % self.title
    
class Staff(models.Model):
    name = models.CharField(max_length=60)

    def __unicode__(self):
        return '%s' % self.name
    
class StaffUser(get_user_model()):
    staff = models.OneToOneField(Staff, related_name='user')
    
    def __unicode__(self):
        return '%s' % self.staff    