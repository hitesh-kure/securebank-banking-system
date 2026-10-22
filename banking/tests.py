from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import BankAccount, Transaction


User = get_user_model()


# -----------------------------------------
# Bank Account Model Tests
# -----------------------------------------

class BankAccountModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testcustomer',
            password='TestPass123!'
        )

    def test_bank_account_creation(self):
        account = BankAccount.objects.create(
            owner=self.user,
            account_number='TEST100001',
            balance=Decimal('5000.00'),
            status='ACTIVE'
        )

        self.assertEqual(account.owner, self.user)
        self.assertEqual(account.account_number, 'TEST100001')
        self.assertEqual(account.balance, Decimal('5000.00'))
        self.assertEqual(account.status, 'ACTIVE')

    def test_new_account_has_zero_balance_by_default(self):
        account = BankAccount.objects.create(
            owner=self.user,
            account_number='TEST100002'
        )

        self.assertEqual(account.balance, Decimal('0.00'))


# -----------------------------------------
# Deposit API Tests
# -----------------------------------------

class DepositAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='depositcustomer',
            password='TestPass123!'
        )

        self.account = BankAccount.objects.create(
            owner=self.user,
            account_number='TEST200001',
            balance=Decimal('1000.00'),
            status='ACTIVE'
        )

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
        )

    def test_successful_deposit(self):
        response = self.client.post(
            '/api/deposit/',
            {
                'account_number': self.account.account_number,
                'amount': '500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.account.refresh_from_db()

        self.assertEqual(self.account.balance, Decimal('1500.00'))
        self.assertEqual(
            Transaction.objects.filter(
                account=self.account,
                transaction_type='DEPOSIT',
                amount=Decimal('500.00')
            ).count(),
            1
        )

    def test_deposit_with_zero_amount_is_rejected(self):
        response = self.client.post(
            '/api/deposit/',
            {
                'account_number': self.account.account_number,
                'amount': '0.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('1000.00'))

    def test_deposit_with_negative_amount_is_rejected(self):
        response = self.client.post(
            '/api/deposit/',
            {
                'account_number': self.account.account_number,
                'amount': '-500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('1000.00'))

    def test_deposit_to_inactive_account_is_rejected(self):
        self.account.status = 'INACTIVE'
        self.account.save()

        response = self.client.post(
            '/api/deposit/',
            {
                'account_number': self.account.account_number,
                'amount': '500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('1000.00'))
        self.assertEqual(
            Transaction.objects.filter(
                account=self.account,
                transaction_type='DEPOSIT'
            ).count(),
            0
        )

    def test_unauthenticated_user_cannot_deposit(self):
        self.client.credentials()

        response = self.client.post(
            '/api/deposit/',
            {
                'account_number': self.account.account_number,
                'amount': '500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('1000.00'))

    def test_deposit_to_nonexistent_account_is_rejected(self):
        response = self.client.post(
            '/api/deposit/',
            {
                'account_number': 'INVALID777777',
                'amount': '500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            Transaction.objects.filter(
                transaction_type='DEPOSIT'
            ).count(),
            0
        )


# -----------------------------------------
# Withdrawal API Tests
# -----------------------------------------

class WithdrawalAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='withdrawcustomer',
            password='TestPass123!'
        )

        self.account = BankAccount.objects.create(
            owner=self.user,
            account_number='TEST300001',
            balance=Decimal('1000.00'),
            status='ACTIVE'
        )

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
        )

    def test_successful_withdrawal(self):
        response = self.client.post(
            '/api/withdraw/',
            {
                'account_number': self.account.account_number,
                'amount': '300.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('700.00'))

        self.assertEqual(
            Transaction.objects.filter(
                account=self.account,
                transaction_type='WITHDRAWAL',
                amount=Decimal('300.00')
            ).count(),
            1
        )

    def test_withdrawal_exceeding_balance_is_rejected(self):
        response = self.client.post(
            '/api/withdraw/',
            {
                'account_number': self.account.account_number,
                'amount': '1500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('1000.00'))

        self.assertEqual(
            Transaction.objects.filter(
                account=self.account,
                transaction_type='WITHDRAWAL'
            ).count(),
            0
        )

    def test_withdrawal_with_zero_amount_is_rejected(self):
        response = self.client.post(
            '/api/withdraw/',
            {
                'account_number': self.account.account_number,
                'amount': '0.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('1000.00'))

    def test_withdrawal_with_negative_amount_is_rejected(self):
        response = self.client.post(
            '/api/withdraw/',
            {
                'account_number': self.account.account_number,
                'amount': '-500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('1000.00'))

    def test_withdrawal_from_inactive_account_is_rejected(self):
        self.account.status = 'INACTIVE'
        self.account.save()

        response = self.client.post(
            '/api/withdraw/',
            {
                'account_number': self.account.account_number,
                'amount': '300.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('1000.00'))

        self.assertEqual(
            Transaction.objects.filter(
                account=self.account,
                transaction_type='WITHDRAWAL'
            ).count(),
            0
        )

    def test_unauthenticated_user_cannot_withdraw(self):
        self.client.credentials()

        response = self.client.post(
            '/api/withdraw/',
            {
                'account_number': self.account.account_number,
                'amount': '300.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('1000.00'))

    def test_withdrawal_from_nonexistent_account_is_rejected(self):
        response = self.client.post(
            '/api/withdraw/',
            {
                'account_number': 'INVALID666666',
                'amount': '300.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            Transaction.objects.filter(
                transaction_type='WITHDRAWAL'
            ).count(),
            0
        )

    def test_refresh_with_invalid_token_is_rejected(self):
        response = self.client.post(
            '/api/token/refresh/',
            {'refresh': 'invalid-refresh-token'},
            format='json'
        )

        self.assertEqual(response.status_code, 401)


# -----------------------------------------
# Transfer API Tests
# -----------------------------------------

class TransferAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='transfercustomer',
            password='TestPass123!'
        )

        self.source_account = BankAccount.objects.create(
            owner=self.user,
            account_number='TEST400001',
            balance=Decimal('2000.00'),
            status='ACTIVE'
        )

        self.destination_account = BankAccount.objects.create(
            owner=self.user,
            account_number='TEST400002',
            balance=Decimal('500.00'),
            status='ACTIVE'
        )

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
        )

    def test_successful_transfer(self):
        response = self.client.post(
            '/api/transfer/',
            {
                'source_account_number': self.source_account.account_number,
                'destination_account_number': self.destination_account.account_number,
                'amount': '500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        self.source_account.refresh_from_db()
        self.destination_account.refresh_from_db()

        self.assertEqual(
            self.source_account.balance,
            Decimal('1500.00')
        )
        self.assertEqual(
            self.destination_account.balance,
            Decimal('1000.00')
        )

        # Sender transaction must remain DEBITED
        self.assertEqual(
            Transaction.objects.filter(
                account=self.source_account,
                transaction_type='DEBITED',
                amount=Decimal('500.00')
            ).count(),
            1
        )

        # Receiver transaction must remain CREDITED
        self.assertEqual(
            Transaction.objects.filter(
                account=self.destination_account,
                transaction_type='CREDITED',
                amount=Decimal('500.00')
            ).count(),
            1
        )

    def test_transfer_exceeding_balance_is_rejected(self):
        response = self.client.post(
            '/api/transfer/',
            {
                'source_account_number': self.source_account.account_number,
                'destination_account_number': self.destination_account.account_number,
                'amount': '5000.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.source_account.refresh_from_db()
        self.destination_account.refresh_from_db()

        self.assertEqual(self.source_account.balance, Decimal('2000.00'))
        self.assertEqual(self.destination_account.balance, Decimal('500.00'))

        self.assertEqual(
            Transaction.objects.filter(
                transaction_type__in=['DEBITED', 'CREDITED']
            ).count(),
            0
        )

    def test_transfer_to_same_account_is_rejected(self):
        response = self.client.post(
            '/api/transfer/',
            {
                'source_account_number': self.source_account.account_number,
                'destination_account_number': self.source_account.account_number,
                'amount': '500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.source_account.refresh_from_db()
        self.assertEqual(self.source_account.balance, Decimal('2000.00'))

        self.assertEqual(
            Transaction.objects.filter(
                transaction_type__in=['DEBITED', 'CREDITED']
            ).count(),
            0
        )

    def test_transfer_from_inactive_account_is_rejected(self):
        self.source_account.status = 'INACTIVE'
        self.source_account.save()

        response = self.client.post(
            '/api/transfer/',
            {
                'source_account_number': self.source_account.account_number,
                'destination_account_number': self.destination_account.account_number,
                'amount': '500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.source_account.refresh_from_db()
        self.destination_account.refresh_from_db()

        self.assertEqual(self.source_account.balance, Decimal('2000.00'))
        self.assertEqual(self.destination_account.balance, Decimal('500.00'))

        self.assertEqual(
            Transaction.objects.filter(
                transaction_type__in=['DEBITED', 'CREDITED']
            ).count(),
            0
        )

    def test_transfer_to_inactive_account_is_rejected(self):
        self.destination_account.status = 'INACTIVE'
        self.destination_account.save()

        response = self.client.post(
            '/api/transfer/',
            {
                'source_account_number': self.source_account.account_number,
                'destination_account_number': self.destination_account.account_number,
                'amount': '500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.source_account.refresh_from_db()
        self.destination_account.refresh_from_db()

        self.assertEqual(self.source_account.balance, Decimal('2000.00'))
        self.assertEqual(self.destination_account.balance, Decimal('500.00'))

        self.assertEqual(
            Transaction.objects.filter(
                transaction_type__in=['DEBITED', 'CREDITED']
            ).count(),
            0
        )

    def test_unauthenticated_user_cannot_transfer(self):
        self.client.credentials()

        response = self.client.post(
            '/api/transfer/',
            {
                'source_account_number': self.source_account.account_number,
                'destination_account_number': self.destination_account.account_number,
                'amount': '500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.source_account.refresh_from_db()
        self.destination_account.refresh_from_db()

        self.assertEqual(self.source_account.balance, Decimal('2000.00'))
        self.assertEqual(self.destination_account.balance, Decimal('500.00'))

    def test_transfer_with_negative_amount_is_rejected(self):
        response = self.client.post(
            '/api/transfer/',
            {
                'source_account_number': self.source_account.account_number,
                'destination_account_number': self.destination_account.account_number,
                'amount': '-500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.source_account.refresh_from_db()
        self.destination_account.refresh_from_db()

        self.assertEqual(self.source_account.balance, Decimal('2000.00'))
        self.assertEqual(self.destination_account.balance, Decimal('500.00'))

    def test_transfer_with_zero_amount_is_rejected(self):
        response = self.client.post(
            '/api/transfer/',
            {
                'source_account_number': self.source_account.account_number,
                'destination_account_number': self.destination_account.account_number,
                'amount': '0.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.source_account.refresh_from_db()
        self.destination_account.refresh_from_db()

        self.assertEqual(self.source_account.balance, Decimal('2000.00'))
        self.assertEqual(self.destination_account.balance, Decimal('500.00'))

    def test_transfer_to_nonexistent_account_is_rejected(self):
        response = self.client.post(
            '/api/transfer/',
            {
                'source_account_number': self.source_account.account_number,
                'destination_account_number': 'INVALID999999',
                'amount': '500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 404)
        self.source_account.refresh_from_db()
        self.assertEqual(self.source_account.balance, Decimal('2000.00'))

        self.assertEqual(
            Transaction.objects.filter(
                transaction_type__in=['DEBITED', 'CREDITED']
            ).count(),
            0
        )

    def test_transfer_from_nonexistent_account_is_rejected(self):
        response = self.client.post(
            '/api/transfer/',
            {
                'source_account_number': 'INVALID888888',
                'destination_account_number': self.destination_account.account_number,
                'amount': '500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 404)
        self.destination_account.refresh_from_db()
        self.assertEqual(self.destination_account.balance, Decimal('500.00'))

        self.assertEqual(
            Transaction.objects.filter(
                transaction_type__in=['DEBITED', 'CREDITED']
            ).count(),
            0
        )


# -----------------------------------------
# Account API Tests
# -----------------------------------------

class AccountAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='accountcustomer',
            password='TestPass123!'
        )

        self.other_user = User.objects.create_user(
            username='othercustomer',
            password='TestPass123!'
        )

        self.account = BankAccount.objects.create(
            owner=self.user,
            account_number='TEST500001',
            balance=Decimal('2500.00'),
            status='ACTIVE'
        )

        self.other_account = BankAccount.objects.create(
            owner=self.other_user,
            account_number='TEST500002',
            balance=Decimal('1000.00'),
            status='ACTIVE'
        )

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
        )

    def test_list_own_accounts(self):
        response = self.client.get('/api/accounts/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['account_number'],
            self.account.account_number
        )

    def test_view_own_account_details(self):
        response = self.client.get(
            f'/api/accounts/{self.account.account_number}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['account_number'],
            self.account.account_number
        )

    def test_check_own_account_balance(self):
        response = self.client.get(
            f'/api/accounts/{self.account.account_number}/balance/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Decimal(str(response.data['balance'])),
            Decimal('2500.00')
        )

    def test_view_own_transaction_history(self):
        Transaction.objects.create(
            account=self.account,
            transaction_type='DEPOSIT',
            amount=Decimal('500.00')
        )

        response = self.client.get(
            f'/api/accounts/{self.account.account_number}/transactions/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(
            response.data['results'][0]['transaction_type'],
            'DEPOSIT'
        )

    def test_cannot_view_another_users_account(self):
        response = self.client.get(
            f'/api/accounts/{self.other_account.account_number}/'
        )

        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_cannot_check_account_balance(self):
        self.client.credentials()

        response = self.client.get(
            f'/api/accounts/{self.account.account_number}/balance/'
        )

        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_cannot_view_transaction_history(self):
        self.client.credentials()

        response = self.client.get(
            f'/api/accounts/{self.account.account_number}/transactions/'
        )

        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_cannot_view_account_details(self):
        self.client.credentials()

        response = self.client.get(
            f'/api/accounts/{self.account.account_number}/'
        )

        self.assertEqual(response.status_code, 401)


# -----------------------------------------
# Banking API Security Tests
# -----------------------------------------

class BankingSecurityAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='securitycustomer',
            password='TestPass123!'
        )

        self.other_user = User.objects.create_user(
            username='othersecuritycustomer',
            password='TestPass123!'
        )

        self.account = BankAccount.objects.create(
            owner=self.user,
            account_number='TEST600001',
            balance=Decimal('5000.00'),
            status='ACTIVE'
        )

        self.other_account = BankAccount.objects.create(
            owner=self.other_user,
            account_number='TEST600002',
            balance=Decimal('3000.00'),
            status='ACTIVE'
        )

    def test_unauthenticated_user_cannot_access_accounts(self):
        response = self.client.get('/api/accounts/')
        self.assertEqual(response.status_code, 401)

    def test_cannot_deposit_into_another_users_account(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
        )

        response = self.client.post(
            '/api/deposit/',
            {
                'account_number': self.other_account.account_number,
                'amount': '500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 404)
        self.other_account.refresh_from_db()
        self.assertEqual(self.other_account.balance, Decimal('3000.00'))

    def test_cannot_withdraw_from_another_users_account(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
        )

        response = self.client.post(
            '/api/withdraw/',
            {
                'account_number': self.other_account.account_number,
                'amount': '500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 404)
        self.other_account.refresh_from_db()
        self.assertEqual(self.other_account.balance, Decimal('3000.00'))

    def test_cannot_transfer_from_another_users_account(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
        )

        response = self.client.post(
            '/api/transfer/',
            {
                'source_account_number': self.other_account.account_number,
                'destination_account_number': self.account.account_number,
                'amount': '500.00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 403)

        self.other_account.refresh_from_db()
        self.account.refresh_from_db()

        self.assertEqual(self.other_account.balance, Decimal('3000.00'))
        self.assertEqual(self.account.balance, Decimal('5000.00'))


# -----------------------------------------
# JWT Authentication Tests
# -----------------------------------------

class JWTAuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jwtcustomer',
            password='TestPass123!'
        )

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            '/api/token/',
            {
                'username': 'jwtcustomer',
                'password': 'TestPass123!',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_invalid_credentials_is_rejected(self):
        response = self.client.post(
            '/api/token/',
            {
                'username': 'jwtcustomer',
                'password': 'WrongPassword123!',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 401)

    def test_refresh_token_returns_new_access_token(self):
        login_response = self.client.post(
            '/api/token/',
            {
                'username': 'jwtcustomer',
                'password': 'TestPass123!',
            },
            format='json'
        )

        self.assertEqual(login_response.status_code, 200)
        refresh_token = login_response.data['refresh']

        response = self.client.post(
            '/api/token/refresh/',
            {'refresh': refresh_token},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)