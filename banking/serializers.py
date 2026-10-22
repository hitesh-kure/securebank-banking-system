
from rest_framework import serializers
from decimal import Decimal
from .models import BankAccount, Transaction


class DepositSerializer(serializers.Serializer):
    account_number = serializers.CharField(
        max_length=20
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01')
    )


class WithdrawalSerializer(serializers.Serializer):
    account_number = serializers.CharField(
        max_length=20
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01')
    )



class TransferSerializer(serializers.Serializer):
    source_account_number = serializers.CharField(
        max_length=20
    )

    destination_account_number = serializers.CharField(
        max_length=20
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01')
    )


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = (
            'account_number',
            'balance',
            'status',
            'created_at',
        )
        read_only_fields = fields



class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'reference',
            'transaction_type',
            'amount',
            'created_at',
        )
        read_only_fields = fields
