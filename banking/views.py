from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db import transaction

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import BankAccount, Transaction
from .serializers import (
    DepositSerializer,
    WithdrawalSerializer,
    TransferSerializer,
    BankAccountSerializer,
    TransactionSerializer,
)


def home(request):
    return HttpResponse("Banking Transaction Management System")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit(request):
    serializer = DepositSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    account_number = serializer.validated_data['account_number']
    amount = serializer.validated_data['amount']

    with transaction.atomic():
        account = get_object_or_404(
            BankAccount.objects.select_for_update(),
            account_number=account_number,
            owner=request.user
        )

        if account.status != 'ACTIVE':
            return Response(
                {'error': 'This bank account is inactive.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        account.balance += amount
        account.save(update_fields=['balance'])

        transaction_record = Transaction.objects.create(
            account=account,
            transaction_type='DEPOSIT',
            amount=amount
        )

    return Response(
        {
            'message': 'Deposit successful.',
            'account_number': account.account_number,
            'deposited_amount': str(amount),
            'new_balance': str(account.balance),
            'transaction_reference': str(transaction_record.reference),
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw(request):
    serializer = WithdrawalSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    account_number = serializer.validated_data['account_number']
    amount = serializer.validated_data['amount']

    with transaction.atomic():
        account = get_object_or_404(
            BankAccount.objects.select_for_update(),
            account_number=account_number,
            owner=request.user
        )

        if account.status != 'ACTIVE':
            return Response(
                {'error': 'This bank account is inactive.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if account.balance < amount:
            return Response(
                {'error': 'Insufficient balance.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        account.balance -= amount
        account.save(update_fields=['balance'])

        transaction_record = Transaction.objects.create(
            account=account,
            transaction_type='WITHDRAWAL',
            amount=amount
        )

    return Response(
        {
            'message': 'Withdrawal successful.',
            'account_number': account.account_number,
            'withdrawn_amount': str(amount),
            'new_balance': str(account.balance),
            'transaction_reference': str(transaction_record.reference),
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer(request):
    serializer = TransferSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    source_number = serializer.validated_data['source_account_number']
    destination_number = serializer.validated_data['destination_account_number']
    amount = serializer.validated_data['amount']

    # Prevent transferring to the same account
    if source_number == destination_number:
        return Response(
            {'error': 'Source and destination accounts must be different.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        # Lock both accounts in a consistent order
        accounts = list(
            BankAccount.objects.select_for_update()
            .filter(
                account_number__in=[
                    source_number,
                    destination_number,
                ]
            )
            .order_by('id')
        )

        account_map = {
            account.account_number: account
            for account in accounts
        }

        source_account = account_map.get(source_number)
        destination_account = account_map.get(destination_number)

        if source_account is None:
            return Response(
                {'error': 'Source account was not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verify source account ownership
        if source_account.owner_id != request.user.id:
            return Response(
                {'error': 'You do not own the source account.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if destination_account is None:
            return Response(
                {'error': 'Destination account was not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Both accounts must be active
        if (
            source_account.status != 'ACTIVE'
            or destination_account.status != 'ACTIVE'
        ):
            return Response(
                {'error': 'Both accounts must be active.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check available balance
        if source_account.balance < amount:
            return Response(
                {'error': 'Insufficient balance.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update both account balances
        source_account.balance -= amount
        destination_account.balance += amount

        source_account.save(update_fields=['balance'])
        destination_account.save(update_fields=['balance'])

        # Record the sender's transaction as DEBITED
        source_transaction = Transaction.objects.create(
            account=source_account,
            transaction_type='DEBITED',
            amount=amount
        )

        # Record the receiver's transaction as CREDITED
        destination_transaction = Transaction.objects.create(
            account=destination_account,
            transaction_type='CREDITED',
            amount=amount
        )

    return Response(
        {
            'message': 'Transfer successful.',
            'amount': str(amount),
            'source_account': source_account.account_number,
            'source_new_balance': str(source_account.balance),
            'destination_account': destination_account.account_number,
            'destination_new_balance': str(destination_account.balance),
            'source_transaction_reference': str(source_transaction.reference),
            'destination_transaction_reference': str(destination_transaction.reference),
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_list(request):
    accounts = BankAccount.objects.filter(owner=request.user)
    serializer = BankAccountSerializer(accounts, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_detail(request, account_number):
    account = get_object_or_404(
        BankAccount,
        account_number=account_number,
        owner=request.user
    )

    serializer = BankAccountSerializer(account)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_balance(request, account_number):
    account = get_object_or_404(
        BankAccount,
        account_number=account_number,
        owner=request.user
    )

    return Response(
        {
            'account_number': account.account_number,
            'balance': str(account.balance),
            'status': account.status,
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history(request, account_number):
    account = get_object_or_404(
        BankAccount,
        account_number=account_number,
        owner=request.user
    )

    transactions = Transaction.objects.filter(
        account=account
    ).order_by('-created_at')

    # Configure pagination: 10 transactions per page
    paginator = PageNumberPagination()
    paginator.page_size = 10

    paginated_transactions = paginator.paginate_queryset(
        transactions,
        request
    )

    serializer = TransactionSerializer(
        paginated_transactions,
        many=True
    )

    return paginator.get_paginated_response(serializer.data)