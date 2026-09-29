from django.db import models
from django.contrib.auth.models import User
class Card(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='cards')
    cardholder_name=models.CharField(max_length=100)
    brand=models.CharField(max_length=30)
    last4=models.CharField(max_length=4)
    masked_number=models.CharField(max_length=25)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.brand} **** {self.last4}'
class Transaction(models.Model):
    STATUS_CHOICES=[('PENDING','Pending'),('SUCCESS','Success'),('FAILED','Failed')]
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='transactions')
    card=models.ForeignKey(Card,on_delete=models.PROTECT,related_name='transactions')
    amount=models.DecimalField(max_digits=12,decimal_places=2)
    currency=models.CharField(max_length=3,default='INR')
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default='PENDING')
    reference=models.CharField(max_length=80,unique=True)
    failure_reason=models.CharField(max_length=255,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self): return self.reference
class AdminLog(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    action=models.CharField(max_length=100)
    details=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
