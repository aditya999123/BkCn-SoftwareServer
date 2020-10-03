from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from sms import send_sms
from keys import *
import hashlib
# Create your views here.

@csrf_exempt
def sign_up(request):
	response_json={}
	if request.method == 'POST':
		try:
			user_name = request.POST.get(keys.KEY_USERNAME)
			hash_pk= hashME(str(request.POST.get(keys.KEY_PK)))
			password = str(request.POST.get(keys.KEY_PASSWORD))
			encoded_password = jwt.encode({keys.KEY_PASSWORD: str(password)}, keys.KEY_PASSWORD_ENCRYPTION,algorithm='HS256')
			try:
				user_instance= UserData.objects.filter(user_name=user_name)
				if user_instance.exists() :
					user_instance = UserData.objects.get(user_name=user_name)
					response_json[keys.KEY_SUCCESS] = False
					response_json[keys.KEY_MESSAGE] = "User Already Exists. Please Login!"
				else:
					temp_access_token = jwt.encode({keys.KEY_ACCESS_TOKEN: str(user_name)},
													keys.KEY_TEMP_ACCESS_TOKEN_ENCRYPTION,
													algorithm='HS256')
					print(temp_access_token)
					user_instance = UserData.objects.create(
															user_name=user_name,
															password=encoded_password,
															hash_pk=hash_pk
															)
					response_json[keys.KEY_TEMP_ACCESS_TOKEN] = temp_access_token
					response_json[keys.KEY_SUCCESS] = True
					response_json[keys.KEY_MESSAGE] = "Sign up complete"
			except Exception as e:
				print str(e)
				response_json[keys.KEY_SUCCESS] = False
				response_json[keys.KEY_MESSAGE] = "Error " + str(e)	
		except Exception as e:
			print str(e)
			response_json[keys.KEY_SUCCESS] = False
			response_json[keys.KEY_MESSAGE] = str(e)
	print response_json
	return JsonResponse(response_json)

@csrf_exempt
def user_login(request):
	if request.method == 'POST':
		response = {}
		try:
			user_name= request.POST.get(keys.KEY_USERNAME)
			password = request.POST.get(keys.KEY_PASSWORD)
			# print password
			encoded_password = jwt.encode({'password': str(password)}, keys.KEY_PASSWORD_ENCRYPTION, algorithm='HS256')
			# print encoded_password
			user_instance = UserData.objects.filter(user_name=user_name, password=encoded_password)
			if user_instance.exists():
				response[keys.KEY_SUCCESS] = True
				response[keys.KEY_MESSAGE] = "Successful"
				access_token = jwt.encode({keys.KEY_ACCESS_TOKEN: str(user_name)}, keys.KEY_ACCESS_TOKEN_ENCRYPTION,
											algorithm='HS256')
				response[keys.KEY_ACCESS_TOKEN] = access_token

			else:
				response[keys.KEY_SUCCESS] = False
				response[keys.KEY_MESSAGE] = "Username and passwords does not match."
		except Exception as e:
			response[keys.KEY_SUCCESS] = False
			response[keys.KEY_MESSAGE] = "Error - " + str(e)
			print(str(e))
	print(response)
	return JsonResponse(response)

def hashMe(msg=""):
	if type(msg)!=str:
		msg = json.dumps(msg,sort_keys=True)  
	if sys.version_info.major == 2:
		return unicode(hashlib.sha256(msg).hexdigest(),'utf-8')
	else:
		return hashlib.sha256(str(msg).encode('utf-8')).hexdigest()