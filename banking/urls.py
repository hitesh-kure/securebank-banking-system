from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/deposit/', views.deposit, name='deposit'), 
    path('api/withdraw/', views.withdraw, name='withdraw'),
    path('api/transfer/', views.transfer, name='transfer'),
    path('api/accounts/', views.account_list, name='account_list'),
    path('api/accounts/<str:account_number>/',
         views.account_detail,
         name='account_detail',),
    path('api/accounts/<str:account_number>/balance/',
         views.account_balance,
         name='account_balance',),
    path(
        'api/accounts/<str:account_number>/transactions/',
        views.transaction_history,
        name='transaction_history',
    ),

]