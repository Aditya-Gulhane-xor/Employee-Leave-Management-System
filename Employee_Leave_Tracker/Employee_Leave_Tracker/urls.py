from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),       # Admin panel
    path('', include('leaves_app.urls')),  # Include your app's URLs
    path('accounts/', include('django.contrib.auth.urls')), # djago authticcation 
    path('api/',include('leaves_app.api_urls')),
    path('api-auth/', include('rest_framework.urls')), #for drf auth for browsable api 
    

]

