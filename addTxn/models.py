from __future__ import unicode_literals

from django.db import models

# Create your models here.
class products_data(models.Model):
	model_no = models.CharField(max_length=255, blank=False, null=False,unique=True)
	type1 = models.CharField(max_length=255, blank=False, null=False)
	product_qty = models.IntegerField(default=0, blank=False, null=False)
	created = models.DateTimeField(auto_now=False, auto_now_add=True)

class model_product_id(models.Model):
	model_no = models.ForeignKey(products_data)
	product_id = models.CharField(max_length=255, blank=False, null=False)
	created = models.DateTimeField(auto_now=False, auto_now_add=True)
	qr=models.ImageField(upload_to='/media/qr_codes',null=True,blank=True)