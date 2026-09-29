from django.urls import path
from .views import *
urlpatterns=[path('auth/register/',register),
             path('auth/me/',me),path('cards/',cards),
             path('cards/<int:pk>/',delete_card),
             path('payments/',payment),path('transactions/',transactions),
             path('admin/export/',export_csv),path('admin/summary/',admin_summary),
             path('admin/users/', admin_users),
             path('admin/users/<int:user_id>/toggle/', admin_toggle_user),
             path('admin/users/<int:user_id>/transactions/', admin_user_transactions)]
