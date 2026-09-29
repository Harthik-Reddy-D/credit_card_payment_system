from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Card,Transaction
class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,min_length=8)
    class Meta: model=User; fields=['username','email','password']
    def create(self,v): return User.objects.create_user(**v)
class UserSerializer(serializers.ModelSerializer):
    class Meta: model=User; fields=['id','username','email','is_staff']
class CardSerializer(serializers.ModelSerializer):
    class Meta: model=Card; fields=['id','cardholder_name','brand','last4','masked_number','created_at']; read_only_fields=['last4','masked_number','created_at']
class AddCardSerializer(serializers.Serializer):
    cardholder_name=serializers.CharField(max_length=100)
    card_number=serializers.CharField(min_length=13,max_length=19)
    brand=serializers.CharField(max_length=30,default='VISA')
    def validate_card_number(self,v):
        digits=''.join(c for c in v if c.isdigit())
        if len(digits) not in range(13,20): raise serializers.ValidationError('Invalid card number')
        return digits
class TransactionSerializer(serializers.ModelSerializer):
    card=CardSerializer(read_only=True)
    class Meta: model=Transaction; fields=['id','reference','amount','currency','status','failure_reason','card','created_at','updated_at']
class PaymentSerializer(serializers.Serializer):
    card_id=serializers.IntegerField()
    amount=serializers.DecimalField(max_digits=12,decimal_places=2,min_value=0.01)
