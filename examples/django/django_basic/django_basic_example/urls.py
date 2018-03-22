from django.contrib import admin
from django.urls import path
from ChattingBox import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('keyboard',views.keyboard),
    path('message', views.message)
]
