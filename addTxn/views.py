from django.shortcuts import render
import pyqrcode
import hashlib, json, sys
from .models import *
import requests
from django.views.decorators.csrf import csrf_exempt
import pdfkit
from django.template.loader import get_template 
from django.template import Context
import urllib
import urllib2

# Create your views here.

def test(request):
	options = {
    'page-size': 'A4',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
	}
	print 'he;llo'
	template = get_template("images.html")
	context = Context({"data": data})  # data is the context data that is sent to the html file to render the output. 
	html = template.render(context)  # Renders the template with the context data.
	pdfkit.from_string(html, 'out.pdf')
	pdf = open("out.pdf")
	response = HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
	response['Content-Disposition'] = 'attachment; filename=output.pdf'
	pdf.close()
	# os.remove("out.pdf")  # remove the locally created pdf file.
 	return response  # returns the response.

def hashMe(msg=""):
	# For convenience, this is a helper function that wraps our hashing algorithm
	if type(msg)!=str:
		msg = json.dumps(msg,sort_keys=True)  # If we don't sort keys, we can't guarantee repeatability!
		
	if sys.version_info.major == 2:
		return unicode(hashlib.sha256(msg).hexdigest(),'utf-8')
	else:
		return hashlib.sha256(str(msg).encode('utf-8')).hexdigest()

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
					qr = pyqrcode.create('id-'+product_id+'\nmodel-'+model_no+'\ntype-'+type1)
					qr.png('media/qr_codes/'+str(model_no)+str(x)+'.png',scale=5)
				list_prod_ids=list_prod_ids+packaging_qr
				if (x>initial):
					qr = pyqrcode.create('id-'+packaging_qr+'\nmodel-'+model_no+'\ntype-'+type1)
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
	url_values = urllib.urlencode(data)
	url = 'central url'
	full_url = url + '?' + url_values
	data = urllib2.urlopen(full_url)

