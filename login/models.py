from __future__ import unicode_literals

from django.db import models


class UserData(models.Model):
	user_name = models.CharField(max_length=255, blank=False, null=False)
	password = models.CharField(max_length=255, blank=False, null=False)
	created = models.DateTimeField(auto_now=False, auto_now_add=True)
	hash_pk = models.CharField(max_length=256,blank=False,null=False)
	public_key=models.CharField(max_length=256)

	def __unicode__(self):
		return self.user_name

# Create your models here.
