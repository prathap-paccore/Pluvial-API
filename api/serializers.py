from rest_framework import serializers 
from  api.models import *
 
class ServiceplanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serviceplan
        fields = '__all__'
        
class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        
class UserFirmsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFirms
        fields = '__all__'

class UserWeatherInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = userWeatherInfo
        fields = '__all__'

class UserWeatherHistoryerializer(serializers.ModelSerializer):
    class Meta:
        model = userWeatherHistory
        fields = '__all__'

class UserOrdersInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = userOrdersInfo
        fields = '__all__'
