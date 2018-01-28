from django.shortcuts import render
import pyqrcode
import hashlib, json, sys
from .models import *
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pdfkit
from django.template.loader import get_template 
from django.template import Context
from django.shortcuts import render
import jwt,zlib

@csrf_exempt
def test1(request):
	response_json={}
	model_no='xyz'
	type1='shoe'
	product_ids=''
	try:
		for x in range (1,10) :
			product_id=hashMe(str(x)+model_no)
			qr = pyqrcode.create('id-'+product_id+'\nmodel-'+model_no+'\ntype-'+type1)
			qr.png('media/qr_codes/'+str(model_no)+str(x)+'.png',scale=5)
			product_ids=product_ids+','+product_id
		print len(product_ids)	
		compressed_ids=product_ids
		print len(compressed_ids)		
		qr = pyqrcode.create('id-'+compressed_ids+'\nmodel-'+model_no+'\ntype-'+type1)
		qr.png('media/qr_codes/'+'pack-'+str(model_no)+str(x)+'.png',scale=5)
		response_json['success']=True
	except Exception as e:
		print str(e)
		response_json['success']=False
	return JsonResponse(response_json)

# Create your views here.
@csrf_exempt
def view_products(request):
	response_json={}
	try:
		response_json['product_list']=[]
		for x in products_data.objects.all():
			temp={}
			temp['model']=x.model_no
			temp['model_qty']=x.product_qty
			temp['type']=x.type1
			response_json['product_list'].append(temp)
		response_json['success']=True
		print response_json
	except Exception as e:
		response_json['success']=False
		response_json['message']=str(e)
	return JsonResponse(response_json)		


@csrf_exempt
def genrateQRCodes(request):
	response_json={}
	if request.method == 'POST':
		try:
			model_no=request.POST.get(keys.KEY_MODEL_NO)
			product_qty=request.POST.get(keys.KEY_PRODUCT_QTY)
			units_per_pack=request.POST.get(keys.KEY_UNITS)
			type1=request.POST.get(keys.KEY_TYPE)
			model_instance=products_data.objects.filter(model_no=model_no)
			if model_instance.exists():
				model_instance=products_data.objects.get(model_no=model_no)
				initial_qty=model_instance.KEY_PRODUCT_QTY
				setattr(model_instance,KEY_PRODUCT_QTY,initial_qty+product_qty)
				model_instance.save()
			else:
				model_row=products_data.objects.create(model_no=model_no,product_qty=product_qty,type1=type1)
			# pk=hashMe(str(request.POST.get('private_key')))
			initial=1

			while(True):
				packaging_qr=''
				for x in range(initial, initial+units_per_pack):
					if(initial>product_qty):
						break
					product_id=hashME(model_no+x+str(datetime.now())+type1)
					product_row =model_product_id.objects.create(model_no=model_no,product_id=product_id)
					product_row.save()
					packaging_qr=packaging_qr+','+str(product_id)
					qr = pyqrcode.create('id-'+product_id+'|'+model_no+'|'+type1)
					qr.png('media/qr_codes/'+str(model_no)+str(x)+'.png',scale=5)
				list_prod_ids=list_prod_ids+packaging_qr
				if (x>initial):
					qr = pyqrcode.create('id-'+packaging_qr+'|'+model_no+'|'+type1)
					qr.png(str('media/qr_codes/'+str(model_no)+str(initial)+'to'+str(x)+'.png'), scale=5)
				initial = x+1;
				if(initial>product_qty):
					break
			sendData2Central(list_prod_ids)		
			response_json['success']=True		
		except Exception as e :
			print str(e)
			response_json['success']=False			
	return JsonResponse(response_json)

def sendData2Central(list_prod_ids):
	data={}
	data['product_ids']=list_prod_ids
	data['public_key']='public_key'
	url = 'http://127.0.0.1:8000/test'
	return requests.post(url,data)