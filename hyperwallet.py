import hyperwallet

from mrsneaker_main.models import Account, Order, Bank, Payment
from django.contrib.auth.models import User


prg = ""
api = hyperwallet.Api("restapiuser@102518221613", "TESTPASSWORD", prg);


# --------------------------------------------------------------------------------------------- #

def create_user(user,type):

    accounts = Account.objects.filter(email=user.email)
    account = accounts.first()



    program_token = prg

    import secrets
    id = secrets.token_hex(32)[0:24]
    account.clientUserId = id
    account.save()

    data = {
        "clientUserId": account.clientUserId,
        "profileType": "INDIVIDUAL",
        "firstName": user.first_name,
        "lastName": user.last_name,
        "dateOfBirth": "1980-01-01",
        "email": user.email,
        "addressLine1": account.street,
        "city": account.city,
        "stateProvince": account.state,
        "country": 'GB',
        "postalCode": account.post_code,
        "programToken": program_token
    };

    status = False

    try:
        response = api.createUser(data);
        account.user_token = response.token
        account.save()
        print('USER CREATED WITH TOKEN ' + response.token)
        status = True
    except Exception as e:
        print(e)
        print('USER CREATION FAILED')

    return status


# --------------------------------------------------------------------------------------------- #


def retrieve_user(user):


    accounts = Account.objects.filter(email=user.email)
    account = accounts.first()


    response = api.getUser(account.user_token);

    token = response.token

    return token



# --------------------------------------------------------------------------------------------- #

def add_bank(user):

    accounts = Account.objects.filter(email = user.email)
    account = accounts.first()

    bank = Bank.objects.filter(account_ID = account.email)
    bank = bank.last()

    print(bank.sort_code)
    print(bank.account_number)

    print(vars(account))

    data = {
        "profileType": "INDIVIDUAL",
        "transferMethodCountry": "GB",
        "transferMethodCurrency": "GBP",
        "type": "BANK_ACCOUNT",
        "bankId": bank.sort_code,
        "bankAccountId": bank.account_number,
        "bankAccountPurpose": "SAVINGS",
        "firstName": user.first_name,
        "lastName": user.last_name,
        "country": "GB",
        "stateProvince": account.state,
        "addressLine1": account.street,
        "city": account.city,
        "postalCode": account.post_code,
        "bankAccountRelationship": "SELF"
    };
    response = api.createBankAccount(account.user_token, data);

    account.bank_token = response.token
    account.save()

    return response.token

# --------------------------------------------------------------------------------------------- #


def add_paypal(user):


    accounts = Account.objects.filter(email=user.email)
    account = accounts.first()

    print(account.user_token)

    data = {
        "type": "PAYPAL_ACCOUNT",
        "transferMethodCountry": "USA",
        "transferMethodCurrency": "USD",
        "email": "test@gmail.com"
    }

    response = api.createPayPalAccount(account.user_token, data);

    account.paypal_token = response.token
    account.save()

    return token

# --------------------------------------------------------------------------------------------- #



def make_payment(order,user,type):
    accounts = Account.objects.filter(email=user.email)
    account = accounts.first()


    if type == 'BANK':
        program_token = prg

        token = account.bank_token

    if type == 'PAYPAL':
        program_token = prg
        token = account.paypal_token


    paymentId = ''
    amount = order.price


    data = {
        "amount": '10',
        "clientPaymentId": "D4444535437543552543534",
        "currency": "GBP",
        "destinationToken": token,
        "programToken": program_token,
        "purpose": "OTHER"
    };

    payment = Payment(email = user.email, clientPaymentId = paymentId, amount = amount)
    payment.save()


    response = api.createPayment(data);
    print('PAYMENT EXECUTED')

# --------------------------------------------------------------------------------------------- #

