from django.urls import include, path
from api import views 
 
urlpatterns = [
    path('', views.myhome), 
    path('api/user/createUser', views.create_user),
    path('api/user/getUsers', views.get_users),
    path('api/user/userLogin', views.user_login),
    path('api/user/updateUserContact', views.updateUserContact),
    path('api/user/getUserDetails', views.user_details),
    path('api/user/deleteUser', views.delete_user),
    path('api/user/changePassword', views.change_userpassword),
    path('api/user/getPlans', views.getplans),
    path('api/user/saveGeometry', views.saveGeometry),
    path('api/user/delGeometry', views.delGeometry),
    path('api/user/getFirms', views.getFirms),
    path('api/user/placeOrder', views.placeOrder),
    path('api/user/fetchImages', views.fetchImages),
    path('api/user/saveFirmStatus', views.saveFirmStatus),
    path('api/user/getWeatherInfo', views.getWeatherInfo),
    path('api/user/placeWeatherOrderJob', views.placeWeatherOrder),
    path('api/user/consolidateWeatherInfoJob', views.consolidateWeatherInfo),
    path('api/user/consolidateWeatherManualInfo', views.consolidateWeatherManualInfo),
    path('api/user/placePlanetOrderJob', views.placePlanetOrderJob),
    path('api/user/orderStatus', views.orderStatus),
    path('api/user/mailSent', views.mailSent),
    path('api/user/resetPassword', views.resetPassword),
    path('<path:path>',views.handleNotFound,name='handleNotFound')
    
    
]