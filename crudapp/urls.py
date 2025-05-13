# crudapp/urls.py

from django.urls import path,include
from . import views

urlpatterns = [
    #path('', views.item_list, name='item_list'),
    path('new/', views.item_create, name='item_create'),
    path('<int:pk>/edit/', views.item_update, name='item_update'),
    path('<int:pk>/delete/', views.item_delete, name='item_delete'),
    path('', views.Suraj, name='Suraj'),

]