from .settings import *
import os

# Configure the domain name using the environment variable
# that Azure automatically creates for us.

#DEBUG = False
#SECRET_KEY = os.environ['SECRET_KEY']
#CSRF_TRUSTED_ORIGINS = ['https://'+ os.environ['WEBSITE_HOSTNAME']] 

ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []

# WhiteNoise configuration
MIDDLEWARE = [                                                                   
    'django.middleware.security.SecurityMiddleware',
# Add whitenoise middleware after the security middleware                             
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',                      
    'django.middleware.common.CommonMiddleware',                                 
    'django.middleware.csrf.CsrfViewMiddleware',                                 
    'django.contrib.auth.middleware.AuthenticationMiddleware',                   
    'django.contrib.messages.middleware.MessageMiddleware',                      
    'django.middleware.clickjacking.XFrameOptionsMiddleware',                    
]

#pluvialWeb,pluvialapiprod
DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'pluvialWeb', 
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host':"mongodb+srv://goe:kPKR99070Ub3T56o@cluster0.np6w8yy.mongodb.net/goe?retryWrites=true&w=majority"
            }
        }
}

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  
STATIC_ROOT = os.path.join(BASE_DIR, 'static')