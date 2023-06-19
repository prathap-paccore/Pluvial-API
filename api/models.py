from djongo import models
import jsonfield
from datetime import datetime
import uuid
from django.contrib.auth.models import AbstractUser
# Create your models here.
#https://stackoverflow.com/questions/48020463/how-can-we-insert-dictionaryjson-in-mongodb-with-django-using-djongo-library


class Serviceplan(models.Model):
    _id=models.ObjectIdField()
    description = models.CharField(max_length=200000)
    plan_type = models.CharField(max_length=500)
    cost=models.IntegerField()
    meas_type= models.CharField(max_length=500)
    is_active = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects=models.DjongoManager()

class Users(AbstractUser):
    _id=models.ObjectIdField()
    username = models.CharField(max_length=500,unique=True)
    customerId= models.CharField(max_length=500,unique=True)
    username = models.CharField(max_length=500,unique=True)
    first_name = models.CharField(max_length=500,blank=True)
    last_name = models.CharField(max_length=500,blank=True)
    email = models.CharField(max_length=500,unique=True)
    password = models.CharField(max_length=500,blank=True)
    phone = models.CharField(max_length=500,blank=True,unique=True)
    is_staff = models.IntegerField(blank=True)
    is_active = models.IntegerField(blank=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_superuser = models.IntegerField(blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    company_name = models.CharField(max_length=500,blank=True)
    address = models.CharField(max_length=500,blank=True)
    address1 = models.CharField(max_length=500,blank=True)
    city = models.CharField(max_length=500,blank=True)
    zip = models.CharField(max_length=500,blank=True)
    state = models.CharField(max_length=500,blank=True)
    country=models.CharField(max_length=500,blank=True)
    credit_card_number = models.CharField(max_length=500,blank=True)
    security_Code = models.CharField(max_length=5, blank=True)
    name_of_card = models.CharField(max_length=500,blank=True)
    expire_month = models.CharField(max_length=500,blank=True)
    expire_year = models.CharField(max_length=500,blank=True)
    billing_address = models.CharField(max_length=500,blank=True)
    status = models.CharField(max_length=500,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    planId = models.EmbeddedField(model_container=Serviceplan,blank=True)
    objects=models.DjongoManager()


class UserFirms(models.Model):
    _id= models.ObjectIdField()
    GlobalID= models.CharField(max_length=100, unique=True)
    CustomerID= models.CharField(max_length=100)
    attributes= jsonfield.JSONField(blank=True)
    geometry= jsonfield.JSONField(blank=True)
    FarmGlobalID= models.CharField(max_length=100, blank=True)    
    status=models.IntegerField() #1 active, 2 delete
    isVerified=models.IntegerField(default=2) #1 verified, 2 un verified
    layerType=models.IntegerField(default=1) #1 feature layer, 2 irrigationLayer
    #createdBy= models.ForeignKey("Users", related_name='createdBy',on_delete=models.CASCADE)
    #updatedBy= models.ForeignKey("Users", related_name='updatedBy',on_delete=models.CASCADE)
    createdBy= models.CharField(max_length=100, blank=True)
    updatedBy= models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=datetime.utcnow)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects=models.DjongoManager()


class userWeatherInfo(models.Model):
    _id= models.ObjectIdField()
    GlobalID= models.CharField(max_length=100)
    weatherInfoRequest= jsonfield.JSONField(blank=True)
    #suneetha = models.JSONField(blank=True)
    #weatherInfoResponse= jsonfield.JSONField(blank=True)
    weatherResults= jsonfield.JSONField(blank=True)
    weatherDate = models.DateTimeField(blank=True)
    extraInfo= jsonfield.JSONField(blank=True)
    createdBy= models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=datetime.utcnow)    
    objects=models.DjongoManager()

class userWeatherHistory(models.Model):
    _id= models.ObjectIdField()
    GlobalID= models.CharField(max_length=100)
    weatherInfoRequest= jsonfield.JSONField(blank=True)
    weatherInfoResponse = models.JSONField(blank=True)
    #weatherResults= jsonfield.JSONField(blank=True)
    #2023-02-25T20:54:00-08:00
    #2023-02-25T21:10:14.070+00:00
    weatherDate = models.DateTimeField(default=datetime.utcnow)
    extraInfo= jsonfield.JSONField(blank=True)
    tmax= models.FloatField(blank=True)
    tmin= models.FloatField(blank=True)
    rh= models.FloatField(blank=True)
    day= models.FloatField(blank=True)
    latitude= models.FloatField(blank=True) #l
    altitude= models.FloatField(blank=True) #z
    uv= models.FloatField(blank=True)
    uz= models.FloatField(blank=True)
    precipitationSummary= models.FloatField(blank=True)
    createdBy= models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=datetime.utcnow)    
    objects=models.DjongoManager()

class userOrdersInfo(models.Model):
    _id= models.ObjectIdField()
    GlobalID= models.CharField(max_length=100)
    order_id=models.CharField(max_length=100, blank=True)
    order_name=models.CharField(max_length=100)
    order_url=models.CharField(max_length=100, blank=True)
    order_status=models.CharField(max_length=100, blank=True) #i,e state - failed, queued, success
    image_ids= jsonfield.JSONField(blank=True)
    geometry= jsonfield.JSONField(blank=True)
    from_date = models.DateTimeField(blank=True)
    to_date = models.DateTimeField(blank=True)
    blobPaths = jsonfield.JSONField(blank=True)
    order_json= jsonfield.JSONField(blank=True)
    extraInfo= jsonfield.JSONField(blank=True)
    status=models.IntegerField(default=1) #1 no orders, 2 queued, 3 success, 4 failed
    createdBy= models.CharField(max_length=100, blank=True)    
    created_at = models.DateTimeField(default=datetime.utcnow)
    updatedBy= models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects=models.DjongoManager()


class userSentMails(models.Model):
    _id= models.ObjectIdField()
    created_at = models.DateTimeField(default=datetime.utcnow)
    token=models.CharField(default=str(uuid.uuid4()), max_length=200)
    email = models.CharField(max_length=500,unique=True)
