
# Create your views here.
from api.models import *
from api.serializers import *
from bson import ObjectId
from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from passlib.handlers.django import django_pbkdf2_sha256 as handler
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser, ParseError
from rest_framework.response import Response
import json
from api.library.commonFunctions import *
from datetime import datetime, timedelta, date
from api.library.weatherApi import *
from api.library.orders import *
from django.utils import (dateformat, formats)
from django.db.models import Q, Avg, Sum, Count
from django.db.models.functions import Cast
import threading
import pytz
import logging.config
from django.core.mail import send_mail
import uuid
from datetime import datetime, timedelta
import jwt
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone



def handleNotFound(request,path) :
    return render(request, '404.html', {})



# logging.basicConfig(filename='./pluvial_logging.log',level=logging.DEBUG, formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S'))
#       Ganesh               #format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(pathname)s:%(lineno)d in ' \
           'function %(funcName)s] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG,
    filename='./pluvial_logging.log'
)

logger = logging.getLogger('flask')
@csrf_exempt
@api_view(["POST"])
def create_user(request):
    resuest_data=request.data
    if (type(resuest_data) is dict) == True :
        resuest_data=resuest_data
        if 'planId' in resuest_data:
            userdatas = Serviceplan.objects.get(_id=ObjectId(resuest_data['planId']))
            user_serializers = ServiceplanSerializer(userdatas, many=False)
            resuest_data['planId']=user_serializers.data
       
    else :
        resuest_data=resuest_data.dict()
        if 'planId' in resuest_data:
            userdatas = Serviceplan.objects.get(_id=ObjectId(resuest_data['planId']))
            user_serializers = ServiceplanSerializer(userdatas, many=False)
            resuest_data['planId']=user_serializers.data
    pass_word=make_password(resuest_data['password'])
    resuest_data['password']=pass_word
    user_count = Users.objects.count()
    if user_count == 0 :
        user_count =1
    else :
        user_count=user_count+1
    formatted_number = str(user_count).zfill(3)
    customerId="PLUCUS"+formatted_number
    resuest_data['customerId']=customerId
    user_serializer = UsersSerializer(data=resuest_data)
    if user_serializer.is_valid():
        user_serializer.save()
        return Response(user_serializer.data, status=200) 
    return Response(user_serializer.errors, status=400)

# @csrf_exempt
@api_view(["GET"])
def get_users(request):
    #cancelOrders = cancelOrder('8d65d5d8-3a28-4b0e-bab8-fc01740bd9ee')
    users=Users.objects.filter(is_active=1)
    users_serializer = UsersSerializer(users, many=True)
    return Response(users_serializer.data,status=200)



# @csrf_exempt
@api_view(['POST'])
def user_login(request) :
        users_data = request.data
        username=users_data['username']
        password=users_data['password']
   
        try: 
            userdata = Users.objects.get(username=username, is_active=1)
        except Users.DoesNotExist: 
            return JsonResponse({'message': ' does not exist'}, status=400)
        userdatas = Users.objects.get(username=username)
        user_serializer = UsersSerializer(userdatas, many=False)
        userObj=user_serializer.data
        pass_word = check_password(password,userObj['password'])
        if pass_word == True :
            users=Users.objects.filter()
            users_serializer = UsersSerializer(users, many=True)
            return JsonResponse({"user":userObj, "users": users_serializer.data},status=200)
        else :
            return JsonResponse({'message': ' does not exist'}, status=400)
  

@csrf_exempt
@api_view(['POST'])
def user_details(request):
    try: 
         users_data = request.data
         username = users_data['username']
         user=Users.objects.get(username=username)
         
    except Users.DoesNotExist: 
        return JsonResponse({'message': ' does not exist'}, status=400)
    userdatas = Users.objects.get(username=username)
    user_serializer = UsersSerializer(userdatas, many=False)
    userFirms=UserFirms.objects.filter(CustomerID=userdatas._id, layerType=1).order_by('-created_at')
    userFirms_serializer = UserFirmsSerializer(userFirms, many=True)
    if userdatas:
        return Response({"userfirms":userFirms_serializer.data, 'userProfile': user_serializer.data},status=200)
    else:
        return Response({'message':"something went wrong"},status=400)

    #return Response(user_serializer.data,status=200)

@csrf_exempt
@api_view(['POST'])
def update_user_details(request):
        resuest_data=request.data
        id=resuest_data['id']
        if (type(resuest_data) is dict) == True :
            resuest_data=resuest_data
        else :
            resuest_data=resuest_data.dict()
        pass_word=make_password(resuest_data['password'])
        resuest_data['password']=pass_word
        userdetails=Users.objects.get(_id=ObjectId(id))
        user_serializer = UsersSerializer(userdetails, data=resuest_data) 
        if user_serializer.is_valid(): 
            user_serializer.save() 
            return Response(user_serializer.data) 
        return Response(user_serializer.errors, status=400)


@csrf_exempt
@api_view(['POST'])
def updateUserContact(request):
        resuest_data=request.data
        id=resuest_data['_id']
        if (type(resuest_data) is dict) == True :
            resuest_data=resuest_data
        else:
            resuest_data=resuest_data.dict()
        
        if 'planId' in resuest_data:
            userdatas = Serviceplan.objects.get(_id=ObjectId(resuest_data['planId']))
            user_serializers = ServiceplanSerializer(userdatas, many=False)
            resuest_data['planId']=user_serializers.data
        
        userdetails=Users.objects.get(_id=ObjectId(id))
        user_serializer = UsersSerializer(userdetails, data=resuest_data,partial=True) 
        if user_serializer.is_valid(): 
            user_serializer.save() 
            return Response(user_serializer.data,status=200) 
        return Response(user_serializer.errors, status=400)

@csrf_exempt
@api_view(['DELETE'])
def delete_user(request):
    resuest_data=request.data
    id=resuest_data['_id']
    # user=Users.objects.get(_id=ObjectId(id))
    # user.delete()
    Users.objects.filter(_id=ObjectId(id)).update(is_active=2)
    return Response({'message': 'User was deleted successfully!'}, status=200)

@csrf_exempt
@api_view(['POST'])
def change_userpassword(request):
        resuest_data=request.data
        id=resuest_data['_id']
        if (type(resuest_data) is dict) == True :
            resuest_data=resuest_data
        else :
            resuest_data=resuest_data.dict()
        users_data =resuest_data
        password=users_data['password']
        id=id
        userdatas = Users.objects.get(_id=ObjectId(id))
        user_serializer = UsersSerializer(userdatas, many=False)
        userObj=user_serializer.data
        if users_data['flag'] == 'changePasswordByAdmin':
            pass_word = True
        else:
            old_password=users_data['old_password']
            pass_word = check_password(old_password,userObj['password'])
        if pass_word == True :
            userObj = Users.objects.get(_id=ObjectId(id))
            pass_wrd=make_password(password)
            userpass={'password':pass_wrd}
            users_serializer = UsersSerializer(userObj, data=userpass,partial=True) 
            if users_serializer.is_valid(): 
                users_serializer.save() 
                return Response(users_serializer.data,status=200)
        else :
                return Response({'message':"old password is not matched"},status=400)


@csrf_exempt
@api_view(['GET'])
def getplans(request):
    plans=Serviceplan.objects.all()
    plan_serializer = ServiceplanSerializer(plans, many=True)
    return Response(plan_serializer.data)


@csrf_exempt
@api_view(['POST'])
def saveGeometry(request):
        
        resuest_data=request.data
        if (type(resuest_data) is dict) == True :
            resuest_data=resuest_data
        else :
            resuest_data=resuest_data.dict()

        try:
        
            json_data = json.loads(resuest_data['requestBody'])
            
            geometry = json_data['geometry']
            attributes = json_data['attributes']
            userId = json_data['userId']
            layerType = json_data['layerType']
            FarmGlobalID = json_data['FarmGlobalID']
            reProjectedcoordinates = coordinatesReproject(geometry['rings'])
            elevation = getElevation(geometry['centroid']['longitude'], geometry['centroid']['latitude'])           
            timezone = getTimeZone(geometry['centroid']['longitude'], geometry['centroid']['latitude']) 
            geometry['centroid'].update({'elevation': elevation})
            geometry.update({'projectedRings': reProjectedcoordinates, 'timezone': timezone})
            isVerified = 2 if layerType == 1 else 1
            userFirm=UserFirms.objects.filter(GlobalID=attributes['GlobalID'], status = 1).first()

            
            
            
            if userFirm:
                dbMOdelData = {
                "GlobalID" : attributes['GlobalID'],
                "CustomerID": attributes['CustomerID'],
                "attributes": attributes,
                "geometry": geometry,
                "FarmGlobalID": FarmGlobalID,
                "status": 1,
                "updatedBy": userId,
                "updated_at": datetime.now(),
                "_id": ObjectId(userFirm._id)
            }
                
                userFirms_serializer = UserFirmsSerializer(userFirm, data=dbMOdelData)
            else:
                dbMOdelData = {
                "GlobalID" : attributes['GlobalID'],
                "CustomerID": attributes['CustomerID'],
                "attributes": attributes,
                "geometry": geometry,
                "FarmGlobalID": FarmGlobalID,
                "status": 1,
                "layerType": layerType,
                "isVerified": isVerified,
                "createdBy": userId,
                "created_at": datetime.now(),
                
            }
                
                userFirms_serializer = UserFirmsSerializer(data=dbMOdelData)

            
            if userFirms_serializer.is_valid():
                
                id = userFirms_serializer.save()
                #print('idddddd', id)
                return Response(userFirms_serializer.data, status=200)
            else:
                print(userFirms_serializer.errors)
                return Response(userFirms_serializer.errors, status=400)

        except Exception as e:
            
            import inspect
            logger.info(('Save Gemorty exception {0} '). format(str(e)))
            logger.info("Save Gemorty Exception raised in line %s" % inspect.trace())
            logger.info("Save GemortyException raised in method %s" % inspect.trace()[-1][3])
            print(e, "exception")
            return Response({'message':str(e)},status=400)

@csrf_exempt
@api_view(['POST'])
def delGeometry(request):
        
        resuest_data=request.data
        if (type(resuest_data) is dict) == True :
            resuest_data=resuest_data
        else :
            resuest_data=resuest_data.dict()

        try:
        
            json_data = json.loads(resuest_data['requestBody'])
            GlobalID = json_data['GlobalID']
            userId = json_data['userId'] 
            
            userFirm=UserFirms.objects.filter(GlobalID=GlobalID, status = 1).update(status=2, isVerified=2,updatedBy=userId, updated_at=datetime.now())
            if userFirm:
                return Response({'message':"Deleted Successfully"},status=200)
                
            else:
                return Response({'message':"something went wrong"},status=400)
        except Exception as e:
            print(e, "exception")
            return Response({'message':str(e)},status=400)



@csrf_exempt
@api_view(['POST'])
def saveFirmStatus(request):
        
        resuest_data=request.data
        if (type(resuest_data) is dict) == True :
            resuest_data=resuest_data
        else :
            resuest_data=resuest_data.dict()

        try:
        
            json_data = json.loads(resuest_data['requestBody'])
            GlobalID = json_data['GlobalID']
            userId = json_data['userId'] 
            isVerified = json_data['isVerified'] 
            
            userFirm=UserFirms.objects.filter(GlobalID=GlobalID, layerType=1).update(isVerified=isVerified, updatedBy=userId, updated_at=datetime.now())
            if userFirm:
                return Response({'message':"updated Successfully"},status=200)
                
            else:
                return Response({'message':"something went wrong"},status=400)
        except Exception as e:
            print(e, "exception")
            return Response({'message':str(e)},status=400)

@csrf_exempt
@api_view(['POST'])
def getWeatherInfo(request):
        
        resuest_data=request.data
        if (type(resuest_data) is dict) == True :
            resuest_data=resuest_data
        else :
            resuest_data=resuest_data.dict()

        try:
            
            json_data = json.loads(resuest_data['requestBody'])
            GlobalID = json_data['GlobalID']

            #userId = json_data['userId'] 
            weatherRecords = []
           
            seven_days_ago = datetime.now() - timedelta(days=15)
    #         {created_at: {
    #     $gte: ISODate("2023-03-12T00:00:00.000000Z"),
    #     $lt: ISODate("2023-03-12T23:00:00.000000Z")
    # }, GlobalID: "4591eaa7-3b82-4dd2-a5e3-288b6ea351d4"}
            records = userWeatherInfo.objects.filter(Q(created_at__gte=seven_days_ago) & Q(created_at__lte=datetime.now()) & Q(GlobalID=GlobalID)).order_by('-weatherDate')
            
            for record in records:
                weatherRecordsDict = {}
                
                weatherRecordsDict['weatherDate']=dateformat.format(record.weatherDate, formats.get_format('m-d-Y'))
                weatherRecordsDict['ETc']=record.weatherResults['ETc']
                weatherRecordsDict['waterDeficiency']=record.weatherResults['waterDeficiency']
                
                weatherRecords.append(weatherRecordsDict)
            if weatherRecords:
                return Response({"weatherRecords":weatherRecords},status=200)
            else:
                return Response({"weatherRecords":weatherRecords},status=400)
        except Exception as e:
            print(e, "exception")
            return Response({'message':str(e)},status=400)



@csrf_exempt
@api_view(['POST'])
def fetchImages(request):
        
        resuest_data=request.data
        if (type(resuest_data) is dict) == True :
            resuest_data=resuest_data
        else :
            resuest_data=resuest_data.dict()

        try:
        
            json_data = json.loads(resuest_data['requestBody'])
            GlobalID = json_data['GlobalID']
            userId = json_data['userId'] 
            userOrders=userOrdersInfo.objects.filter(GlobalID=GlobalID, status=3).order_by('-from_date')
            
            imageDates = {}
            for userOrder in userOrders:
                imageDates[userOrder.order_id+","+userOrder.blobPaths['blobImageUrl']+","+userOrder.blobPaths['blobNDVIUrl']] = \
                dateformat.format(userOrder.from_date, formats.get_format('m-d-Y'))
                
            if imageDates:
                return Response({"imageDates":imageDates},status=200)
            else:
                return Response({"imageDates":imageDates},status=400)
        except Exception as e:
            print(e, "exception")
            return Response({'message':str(e)},status=400)


@api_view(['GET'])
def orderStatus(request):
    try:
        userOrders=userOrdersInfo.objects.filter(status=2)
        records = []
        for userOrder in userOrders:
            print("OrderStatus")
            orderResults = orderUpload(userOrder.order_id)
            orderResults.update({'updated_at': datetime.now()})
            userOrders=userOrdersInfo.objects.filter(order_id=userOrder.order_id, status=2).update(**orderResults)
            records.append(orderResults)
        return Response({'data': records},status=200)
    except Exception as e:
        print(e, "exception")
        return Response({'message':str(e)},status=400)

def orderStatusThread(userId):
    try:
        logger = logging.getLogger('flask')
        
        userOrders=userOrdersInfo.objects.filter(status=2)
        logger.info('*************userOrders ******************')
        logger.info(('userOrders Info{0} '). format(userOrders))
        #orderResults = orderUpload("f4a31a5f-8900-4c01-b13e-fd57060c9310")
        
        
        records = []
        for userOrder in userOrders:
            print("OrderStatus")
            orderResults = orderUpload(userOrder.order_id)
            
            orderResults.update({'updatedBy': userId,'updated_at': datetime.now()})
            logger.info(('orderResults Info{0} '). format(orderResults))
            userOrders=userOrdersInfo.objects.filter(order_id=userOrder.order_id, status=2).update(**orderResults)
            records.append(orderResults)
        #print(records)
    except Exception as e:
        print(e, "exception")
        logger.info(('orderStatusThread exception Info{0} '). format(str(e)))


@csrf_exempt
@api_view(['POST'])
def getFirms(request):
        
        resuest_data=request.data
        if (type(resuest_data) is dict) == True :
            resuest_data=resuest_data
        else :
            resuest_data=resuest_data.dict()
        
        
        try:  
            #69d79258-e91c-4684-a4d1-6d8654860dce - failed
            #a983ddc3-556b-46e6-84a8-c55f600d8332 - without zip success
            #4e764312-1bc4-4ab2-9b62-ace811d851ec - zip with success
            #{"userId":"6386a0de2b3de2a0010e2833"}
            logger = logging.getLogger('flask')
            logger.info('*************orderStatusThread ******************')

            _thread = threading.Thread(target=orderStatusThread, args=(resuest_data['userId'],))
            _thread.start()
            logger.info('*************order Status Thread start******************')
            userFirms=UserFirms.objects.filter(isVerified=1, status = 1, layerType=1)
            user_firms_serializer = UserFirmsSerializer(userFirms, many=True)
            userOrders=userOrdersInfo.objects.order_by('-created_at')
            user_orders_serializer = UserOrdersInfoSerializer(userOrders, many=True)
            if userFirms:
                return Response({"firms":user_firms_serializer.data, 'orders': user_orders_serializer.data},status=200)
                
            else:
                return Response({'message':"something went wrong"},status=400)
        except Exception as e:
            print(e, "exception")
            return Response({'message':str(e)},status=400)



@api_view(['GET'])
def placeWeatherOrder(request):
    try:
        
        userFirms = UserFirms.objects.filter(status = 1, isVerified=1)

        weatherRecordss = []
        for userFirm in userFirms:

            #geometrycoordinates = userFirm.geometry['projectedRings']
            centroid_lat = userFirm.geometry['centroid']['latitude']
            centroid_long= userFirm.geometry['centroid']['longitude']
            elevation = userFirm.geometry['centroid']['elevation']
            weatherResults= callWeatherAPI(centroid_long,centroid_lat,elevation)
            weatherResults.update({'GlobalID':userFirm.GlobalID,'created_at':datetime.now()})
            
            #userWeatherHistory UserWeatherHistoryerializer
            user_weather_serializer = UserWeatherHistoryerializer(data=weatherResults)
            if user_weather_serializer.is_valid():    
                id = user_weather_serializer.save()
                weatherRecordss.append(weatherResults)                       
            else:
                print(user_weather_serializer.errors)
        return Response({"weatherRecords": weatherRecordss},status=200)
                
    except Exception as e:
        return Response({'message':str(e)},status=400)


@api_view(['GET'])
def consolidateWeatherInfo(request):
    try:
        
        userFirms = UserFirms.objects.filter(status = 1, isVerified=1)

        weatherRecordss = []
        for userFirm in userFirms:

            d = datetime.now()
            weatherInfoDict = {}
            results = {}
            weatherDate = ''
            #mydate = datetime.strptime('2023-03-01T17:04:00-08:00', '%Y-%m-%dT%H:%M:%S%z')
    
            historyresults = userWeatherHistory.objects \
            .filter(GlobalID=userFirm.GlobalID, created_at__gte=d.date(), 
                    created_at__lt=d.date()+timedelta(days=1)
                    ) \
            .values('GlobalID', 'day', 'tmax','tmin','latitude','altitude', 'precipitationSummary') \
            .annotate(uz=Avg('uz'), uv=Avg('uv'), rh=Avg('rh')) 
            
            if historyresults:
                result = historyresults[0]
                weatherInfoDict = {
                "tmax" : result['tmax'],
                "tmin" : result['tmin'],
                "rh" : result['rh'],
                "day" : result['day'],
                "latitude" : result['latitude'], #l
                "altitude" : result['altitude'], #z
                'precipitationSummary':result['precipitationSummary'],
                "uv" :result['uv'],
                "uz" : result['uz'],  
                "albedo" : float(0.23),
                "cd" : float(0.28),
                "cn" : float(1600),
                "kc" : float(0.40),
            }
            #print(weatherInfoDict, 'weatherInfoDict')
                results = calcEvaportation(weatherInfoDict)
                #weatherDate = result['weatherDate']
                weatherDate = datetime.now()
	

            finalresults = {}
            finalresults.update({'weatherInfoRequest': weatherInfoDict,
                            'weatherResults': results,
                            'GlobalID':userFirm.GlobalID,
                            'weatherDate':weatherDate,
                            'created_at':datetime.now(),
                            'extraInfo': {"albedo" : float(0.23),"cd" : float(0.28), "cn" : float(1600),"kc" : float(0.40)}
                            })
            
            #userWeatherHistory UserWeatherHistoryerializer
            user_weather_serializer = UserWeatherInfoSerializer(data=finalresults)
            if user_weather_serializer.is_valid():    
                id = user_weather_serializer.save()
                weatherRecordss.append(results)                       
            else:
                print(user_weather_serializer.errors)
        return Response({"weatherRecords": weatherRecordss},status=200)
                
    except Exception as e:
        return Response({'message':str(e)},status=400)
 

@api_view(['GET'])
def consolidateWeatherManualInfo(request):
    try:
    #     {created_at: {
    #     $gte: ISODate("2023-03-22T00:00:00.290608Z"),
    #     $lt: ISODate("2023-03-22T23:47:25.263714Z")
    # }, 'GlobalID': "2fa2f216-35d1-4b57-b11c-7a76a2a5ad6f"}
        
        userFirms = UserFirms.objects.filter(status = 1, isVerified=1)

        weatherRecordss = []
        for userFirm in userFirms:
            #2023-03-25 15:22:34.975263
            # d = datetime.strptime('2023-03-19 06:45:34.975263', '%Y-%m-%d %H:%M:%S.%f')
            # print(d.date())
            d = datetime.strptime('2023-03-19T06:45:00-08:00', '%Y-%m-%dT%H:%M:%S%z')
            weatherInfoDict = {}
            results = {}
            weatherDate = ''
            #mydate = datetime.strptime('2023-03-01T17:04:00-08:00', '%Y-%m-%dT%H:%M:%S%z')
    
            historyresults = userWeatherHistory.objects \
            .filter(GlobalID=userFirm.GlobalID, created_at__gte=d.date(), 
                    created_at__lt=d.date()+timedelta(days=1)
                    ) \
            .values('GlobalID', 'day', 'tmax','tmin','latitude','altitude', 'precipitationSummary') \
            .annotate(uz=Avg('uz'), uv=Avg('uv'), rh=Avg('rh')) 
            
            if historyresults:
                result = historyresults[0]
                weatherInfoDict = {
                "tmax" : result['tmax'],
                "tmin" : result['tmin'],
                "rh" : result['rh'],
                "day" : result['day'],
                "latitude" : result['latitude'], #l
                "altitude" : result['altitude'], #z
                'precipitationSummary':result['precipitationSummary'],
                "uv" :result['uv'],
                "uz" : result['uz'],  
                "albedo" : float(0.23),
                "cd" : float(0.28),
                "cn" : float(1600),
                "kc" : float(0.40),
            }
            #print(weatherInfoDict, 'weatherInfoDict')
                results = calcEvaportation(weatherInfoDict)
                #weatherDate = result['weatherDate']
                weatherDate = d
	

            finalresults = {}
            finalresults.update({'weatherInfoRequest': weatherInfoDict,
                            'weatherResults': results,
                            'GlobalID':userFirm.GlobalID,
                            'weatherDate':weatherDate,
                            'created_at':d,
                            'extraInfo': {"albedo" : float(0.23),"cd" : float(0.28), "cn" : float(1600),"kc" : float(0.40)}
                            })
            
            #userWeatherHistory UserWeatherHistoryerializer
            user_weather_serializer = UserWeatherInfoSerializer(data=finalresults)
            if user_weather_serializer.is_valid():    
                id = user_weather_serializer.save()
                weatherRecordss.append(results)                       
            else:
                print(user_weather_serializer.errors)
        return Response({"weatherRecords": weatherRecordss},status=200)
                
    except Exception as e:
        return Response({'message':str(e)},status=400)
 


@csrf_exempt
@api_view(['POST'])
def placeOrder(request):
    resuest_data=request.data
    if (type(resuest_data) is dict) == True :
        resuest_data=resuest_data
    else :
        resuest_data=resuest_data.dict()

    try:
        
        
        planetResultsDict = {}
        weatherResults = {}
        userFirm=UserFirms.objects.get(GlobalID=resuest_data['GlobalID'], status = 1, isVerified=1, layerType=1)        
        geometrycoordinates = userFirm.geometry['projectedRings']
        """
        centroid_lat = userFirm.geometry['centroid']['latitude']
        centroid_long= userFirm.geometry['centroid']['longitude']
        elevation = userFirm.geometry['centroid']['elevation']
        weatherResults= callWeatherAPI(centroid_long,centroid_lat,elevation)
        weatherResults.update({'GlobalID':resuest_data['GlobalID'], 'createdBy': resuest_data['userId'], 'created_at':datetime.now()})
        
        
        user_weather_serializer = UserWeatherInfoSerializer(data=weatherResults)
        if user_weather_serializer.is_valid():    
            id = user_weather_serializer.save()                       
        else:
            print(user_weather_serializer.errors) 
        """
        
        date = resuest_data['fromDate'].split('T')[0]
        fromDate = resuest_data['fromDate']+":00Z"
        toDate = resuest_data['fromDate'].split('T')[0]+"T23:59:00Z"
        orderName = userFirm.attributes['FarmName']+"_"+date
        planetResults = placePlanetOrder(orderName, geometrycoordinates, fromDate, toDate )
        
        if planetResults['flag']:            
            planetResultsDict = {
                'GlobalID':resuest_data['GlobalID'],
                'order_id':planetResults['order_id'], 
                'order_name': orderName,
                'order_url':planetResults['order_url'], 
                "order_status": planetResults['order_status'] ,
                'image_ids':planetResults['image_ids'],
                 'geometry':geometrycoordinates,
                 'from_date':fromDate,
                 "to_date": toDate,
                 "status": 2,
                 'createdBy': resuest_data['userId'], 
                 'created_at':datetime.now()
            }
        else:
            planetResultsDict = {
                'GlobalID':resuest_data['GlobalID'],                
                'order_name': orderName,               
                'image_ids':planetResults['image_ids'],
                "order_status": planetResults['order_status'],  #order_status
                 'geometry':geometrycoordinates,
                 'from_date':fromDate,
                 "to_date": toDate,
                 "status": 1,
                 'createdBy': resuest_data['userId'], 
                 'created_at':datetime.now()
            }
       
        user_order_serializer = UserOrdersInfoSerializer(data=planetResultsDict)
        if user_order_serializer.is_valid():    
            id = user_order_serializer.save()
            userFirms=UserFirms.objects.filter(isVerified=1, status = 1, layerType=1)
            user_firms_serializer = UserFirmsSerializer(userFirms, many=True)
            userOrders=userOrdersInfo.objects.order_by('-created_at')
            user_orders_serializer = UserOrdersInfoSerializer(userOrders, many=True)
            if id and userFirms:
                #orderStatus(resuest_data['userId'])
                _thread = threading.Thread(target=orderStatusThread, args=(resuest_data['userId'],))
                _thread.start()
                return Response({"firms":user_firms_serializer.data, 'orders': user_orders_serializer.data},status=200)
                
            else:
                return Response({'message':"something went wrong"},status=400)

            
        else:
            print(user_order_serializer.errors)
            return Response(user_order_serializer.errors, status=400)
    except Exception as e:
        print(e, "exception")
        return Response({'message':str(e)},status=400)
    

@csrf_exempt
@api_view(['GET'])
def placePlanetOrderJob(request):
    

    try:
        
        
        planetResultsDict = {}
        weatherResults = {}
        userFirms = UserFirms.objects.filter(status = 1, isVerified=1, layerType=1)

        planetRecordss = []
        for userFirm in userFirms:
            
            geometrycoordinates = userFirm.geometry['projectedRings']
            
            timezone = userFirm.geometry['timezone']
            firmTz = pytz.timezone(timezone) 
            timeInFirm = datetime.now(firmTz)
            past_24_hours_Time = timeInFirm - timedelta(hours=24)
            past_24_hours_date = past_24_hours_Time.strftime("%Y-%m-%d")

            #past_24_hours = date.today() - timedelta(hours=24)
            #current_date = date.today()
            fromDate = str(past_24_hours_date)+"T00:00:00Z"
            toDate = str(past_24_hours_date)+"T23:59:00Z"

            orderName = userFirm.attributes['FarmName']+"_"+str(past_24_hours_date)
            
            logger = logging.getLogger('flask')

            logger.info('*************User Firm Orders Request Start******************')

            logger.info(('Request Order Name: {0} \n'
                            'geometrycoordinates: {1} \n'
                            'fromDate: {2} \n'
                            'toDate: {3} \n').format(orderName,
                                                            geometrycoordinates,
                                                            fromDate,
                                                            toDate))

            
            planetResults = placePlanetOrder(orderName, geometrycoordinates, fromDate, toDate )
            logger.info('*************User Firm Orders Request End******************')
            if planetResults['flag']:            
                planetResultsDict = {
                    'GlobalID':userFirm.GlobalID,
                    'order_id':planetResults['order_id'], 
                    'order_name': orderName,
                    'order_url':planetResults['order_url'], 
                    "order_status": planetResults['order_status'] ,
                    'image_ids':planetResults['image_ids'],
                    'geometry':geometrycoordinates,
                    'from_date':fromDate,
                    "to_date": toDate,
                    "status": 2,
                    #'createdBy': resuest_data['userId'], 
                    'created_at':datetime.now()
                }
            else:
                planetResultsDict = {
                    'GlobalID':userFirm.GlobalID,                
                    'order_name': orderName,               
                    'image_ids':planetResults['image_ids'],
                    "order_status": planetResults['order_status'],  #order_status
                    'geometry':geometrycoordinates,
                    'from_date':fromDate,
                    "to_date": toDate,
                    "status": 1,
                    #'createdBy': resuest_data['userId'], 
                    'created_at':datetime.now()
                }
        
            user_order_serializer = UserOrdersInfoSerializer(data=planetResultsDict)
            if user_order_serializer.is_valid():    
                id = user_order_serializer.save()
                planetRecordss.append(weatherResults)
            else:
                print(user_order_serializer.errors)
                return Response(user_order_serializer.errors, status=400)
        return Response({"planetRecords": planetRecordss},status=200)
    except Exception as e:
        print(e, "exception")
        return Response({'message':str(e)},status=400)

@api_view(["GET"])
def myhome(request): 
    return render(request, 'home.html', {})



@api_view(['POST'])
def mailSent(request):
    try:
        resuest_data=request.data
        if (type(resuest_data) is dict) == True :
            resuest_data=resuest_data
        else :
            resuest_data=resuest_data.dict()
        email=resuest_data['email']
        email_detail = Users.objects.filter(email=email).first()
        if email_detail:
            id=email_detail._id
            id=str(id)
            exp=datetime.utcnow() + timedelta(days=0,minutes=10,seconds=0)
            iat=datetime.utcnow()
            token = jwt.encode({"userId": id,'exp':exp,'iat':iat}, settings.JWT_SECRET, algorithm="HS256")
            subject = "Pluvial forgotpassword generated mail"
            message = (
                f"Hi   reset your password "+settings.FE_URL+"pluvialUser/resetPasswordLink/"
                + token
                + " Thanks."
            )
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email_detail.email]
            send_mail(subject, message, email_from, recipient_list, token)
            return JsonResponse({'message': 'Sent Mail '}, status=200)
        else:
            return JsonResponse({'message': ' does not exist'}, status=400)
    except Exception as e:
        print(e, "exception")
        return Response({'message':str(e)},status=400)



@api_view(['POST'])
def resetPassword(request):
    resuest_data=request.data
    if (type(resuest_data) is dict) == True :
        resuest_data=resuest_data
    else :
        resuest_data=resuest_data.dict()
    password=resuest_data['password']
    token=resuest_data['token']
    try:

        data = jwt.decode(token, settings.JWT_SECRET, algorithms='HS256')
        userId=data['userId']
        exp=data['exp']
        now=datetime.utcnow()
        userdatas = Users.objects.get(_id=ObjectId(userId))
        if userdatas :
            userObj = Users.objects.get(_id=ObjectId(userId))
            pass_wrd=make_password(password)
            userpass={'password':pass_wrd}
            users_serializer = UsersSerializer(userObj, data=userpass,partial=True) 
            if users_serializer.is_valid(): 
                users_serializer.save() 
                return Response(users_serializer.data,status=200)
            else:
                return JsonResponse({'message': ' does not exist'}, status=400)
        
        else:
                return Response({'message':"Invalid Details"},status=400)
    except Exception as e:
        print(e, "exception")
        return Response({'message':str(e)},status=400)
