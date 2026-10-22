from django.contrib import admin
from .models import BankAccount, Transaction


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'account_number',
        'owner',
        'balance',
        'status',
        'created_at',
    )

    search_fields = (
        'account_number',
        'owner__username',
    )

    list_filter = ('status',)
    

    @admin.register(Transaction)
    class TransactionAdmin(admin.ModelAdmin):
        list_display = (
            'id',
            'reference',
            'account',
            'transaction_type',
            'amount',
            'created_at',
        )

        search_fields = (
            'refrence',
            'account_account_number',
        )

        list_filter = (
            'transaction_type',
            'created_at',
        )

        readonly_fields = (
            'reference',
            'created_at',
        )