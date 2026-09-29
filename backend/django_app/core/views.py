import csv, os, uuid, requests
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Card, Transaction, AdminLog
from .serializers import *
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    s=RegisterSerializer(data=request.data); s.is_valid(raise_exception=True); u=s.save(); return Response(UserSerializer(u).data,status=201)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request): return Response(UserSerializer(request.user).data)
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def cards(request):
    if request.method=='GET': return Response(CardSerializer(Card.objects.filter(user=request.user),many=True).data)
    s=AddCardSerializer(data=request.data); s.is_valid(raise_exception=True); d=s.validated_data; num=d['card_number']; last4=num[-4:]; masked='*'*(len(num)-4)+last4
    c=Card.objects.create(user=request.user,cardholder_name=d['cardholder_name'],brand=d['brand'],last4=last4,masked_number=masked)
    return Response(CardSerializer(c).data,status=201)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_card(request,pk):
    try: c=Card.objects.get(pk=pk,user=request.user)
    except Card.DoesNotExist: return Response(status=404)
    if c.transactions.exists(): return Response({'detail':'Card has transactions and cannot be deleted.'},status=400)
    c.delete(); return Response(status=204)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payment(request):
    s=PaymentSerializer(data=request.data); s.is_valid(raise_exception=True); d=s.validated_data
    try: card=Card.objects.get(id=d['card_id'],user=request.user)
    except Card.DoesNotExist: return Response({'detail':'Card not found'},status=404)
    tx=Transaction.objects.create(user=request.user,card=card,amount=d['amount'],reference='TXN-'+uuid.uuid4().hex[:12].upper())
    url=os.getenv('PAYMENT_SERVICE_URL','http://payment-service:8000')+'/simulate-payment'
    try:
        r=requests.post(url,json={'amount':float(tx.amount),'reference':tx.reference},timeout=10); r.raise_for_status(); result=r.json()
        tx.status=result['status']; tx.failure_reason=result.get('reason',''); tx.save(update_fields=['status','failure_reason','updated_at'])
    except Exception as e:
        tx.status='FAILED'; tx.failure_reason='Payment service unavailable'; tx.save(update_fields=['status','failure_reason','updated_at'])
    return Response(TransactionSerializer(tx).data,status=201)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transactions(request):
    qs=Transaction.objects.filter(user=request.user).select_related('card')
    if request.GET.get('status'): qs=qs.filter(status=request.GET['status'].upper())
    if request.GET.get('min_amount'): qs=qs.filter(amount__gte=request.GET['min_amount'])
    if request.GET.get('max_amount'): qs=qs.filter(amount__lte=request.GET['max_amount'])
    if request.GET.get('date'): qs=qs.filter(created_at__date=request.GET['date'])
    return Response(TransactionSerializer(qs,many=True).data)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def export_csv(request):
    qs=Transaction.objects.select_related('user','card').all(); resp=HttpResponse(content_type='text/csv'); resp['Content-Disposition']='attachment; filename="transactions.csv"'; w=csv.writer(resp); w.writerow(['Reference','User','Amount','Currency','Status','Card Last4','Created'])
    for t in qs: w.writerow([t.reference,t.user.username,t.amount,t.currency,t.status,t.card.last4,t.created_at.isoformat()])
    return resp
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_summary(request):
    from django.db.models import Sum,Count
    return Response({'transactions':Transaction.objects.count(),'users':User.objects.count(),'cards':Card.objects.count(),'successful_amount':Transaction.objects.filter(status='SUCCESS').aggregate(v=Sum('amount'))['v'] or 0,'success_count':Transaction.objects.filter(status='SUCCESS').count(),'failed_count':Transaction.objects.filter(status='FAILED').count()})
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')

    data = []

    for user in users:
        data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'date_joined': user.date_joined,
        })

    return Response(data)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def admin_toggle_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if user.id == request.user.id:
        return Response(
            {'detail': 'You cannot disable your own account.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])

    return Response({
        'id': user.id,
        'is_active': user.is_active
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_user_transactions(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    transactions = Transaction.objects.filter(
        user=user
    ).order_by('-created_at')

    serializer = TransactionSerializer(
        transactions,
        many=True
    )

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
        'transactions': serializer.data
    })