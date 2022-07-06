import os
import requests
import json
from mrsneaker_main.models import Account, Order, Bank, product_reserve, fees, Card, Shipping, open_offer



import OpenSSL
from OpenSSL import crypto
import base64


class InternationalPayment:

    def __init__(self):

        self.quote_id = None
        self.customer_id = None
        self.transfer_id = None
        self.API_TOKEN = ''
        self.profile = ''
        self.order = None

    def order_type(self,order):

        order_number = ''

        if order.sell_sneakers == True:
            order_number = 'MRR' + order.order_number[1:]

        if order.consign_sneakers == True:
            order_number = 'MRC' + order.order_number[1:]

        return order_number



    def create_quote(self,currency_code,order):

        fee_objects = fees.objects.all()
        fee_object = fee_objects.last()

        transaction_fee = (float(order.price) / 100) * float(fee_object.transaction_fee)
        processing_fee = (float(order.price) / 100) * float(fee_object.processing_fee)

        if currency_code == 'USD':

            if order.consign_sneakers == True:
                price = (float(order.price) / 100)
                price = float(payout * 80.0)
                p = (0.35 / 100) * p
                price = float(float(price) + p + 0.35)

            else:

                p = float(order.price)
                p = (0.35 / 100) * p
                price = float(float(order.price) + p + 0.35)

        if currency_code == 'EUR':

            if order.consign_sneakers == True:
                price = (float(order.price) / 100)
                price = float(payout * 80.0)
                p = (0.35 / 100) * p
                price = float(float(price) + p + 0.20)



            else:
                p = float(order.price)
                p = (0.35 / 100) * p
                price = float(float(order.price) + p + 0.20)








        url = 'https://api.transferwise.com/v2/quotes'

        data = {
                  "sourceCurrency": "GBP",
                  "targetCurrency": currency_code,
                  "sourceAmount": price,
                  "targetAmount": None,
                  "profile": self.profile,
                }


        data = json.dumps(data)

        result = requests.post(url,
              headers={'Content-Type':'application/json',
                       'Authorization': 'Bearer {}'.format(self.API_TOKEN)}, data = data)



        data = json.loads(result.text)
        quote_id = data['id']

        self.quote_id = quote_id
        self.order = order

        print('QUOTE CREATED')



    def create_recipient(self,currency_code,bank,user):

        shipping = Shipping.objects.all().filter(email = user.email).first()

        if shipping.country == 'United States':

            data = {
            "profile": self.profile,
            "accountHolderName": user.first_name + ' ' + user.last_name,
            "currency": currency_code,
            "type": "aba",
            "details": {
                "legalType": "PRIVATE",
                "abartn": bank.routing_number,
                "accountNumber": bank.account_number,
                "accountType": "CHECKING",
                "address": {
                    "country": "GB",
                    "city": "London",
                    "postCode": "10025",
                    "firstLine": "50 Branson Ave"
                }
            }

            }

        else:

            data = {
            "profile": self.profile,
            "accountHolderName": user.first_name + ' ' + user.last_name,
            "currency": currency_code,
            "type": "iban",
            "details": {
                "legalType": "PRIVATE",
                "iban": bank.iban,
                "address": {
                    "country": "GB",
                    "city": "London",
                    "postCode": "10025",
                    "firstLine": "50 Branson Ave"
                }
            }

            }


        data = json.dumps(data)

        url = 'https://api.transferwise.com/v1/accounts'

        result = requests.post(url,
                               headers={'Content-Type': 'application/json',
                                        'Authorization': 'Bearer {}'.format(self.API_TOKEN)}, data=data)

        print(result)
        print(result.text)


        data = json.loads(result.text)

        self.customer_id = data['id']





    def create_transfer(self):

        import uuid

        order_number = self.order_type(self.order)



        data = {
          "targetAccount": self.customer_id,
          "quoteUuid": self.quote_id,
          "customerTransactionId": str(uuid.uuid4()),
          "details" : {
              "reference": order_number,
              "transferPurpose": "verification.transfers.purpose.pay.bills",
              "sourceOfFunds": "verification.source.of.funds.other"
            }
         }

        data = json.dumps(data)

        url = 'https://api.transferwise.com/v1/transfers'

        result = requests.post(url,
                               headers={'Content-Type': 'application/json',
                                        'Authorization': 'Bearer {}'.format(self.API_TOKEN)}, data=data)


        data = json.loads(result.text)

        print(result.text)

        self.transfer_id = data['id']



    def fund_transfer(self):

        data = {
          "type": "BALANCE"
         }

        data = json.dumps(data)


        url = 'https://api.transferwise.com/v3/profiles/' + str(self.profile) + '/transfers/'+ str(self.transfer_id) +'/payments'


        result = requests.post(url,
                               headers={'Content-Type': 'application/json',
                                        'Authorization': 'Bearer {}'.format(self.API_TOKEN)}, data=data)

        approval = result.headers['x-2fa-approval']

        key_file = open("private.pem", "rb")
        key = key_file.read()
        key_file.close()

        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key)


        dataBytes = bytes(approval, encoding='ascii')

        signData = OpenSSL.crypto.sign(pkey, dataBytes, "sha256")

        encodedData = base64.b64encode(signData)

        result = requests.post(url,
                               headers={'Content-Type': 'application/json',
                                        'Authorization': 'Bearer {}'.format(self.API_TOKEN),'x-2fa-approval': approval, 'X-Signature': encodedData}, data=data)


        print(result)
        print(result.text)
        print(result.headers)







