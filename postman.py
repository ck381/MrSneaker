# Make sure to install requests: pip install requests
from __future__ import print_function

import requests
from credentials import *
import pprint
from postmen import Postmen, PostmenException
from mrsneaker_main.models import Account, Order, Shipping
from django.contrib.auth.models import User
import json
from postmen import Postmen, PostmenException


pp = pprint.PrettyPrinter(indent=4)


api_key = ''

region = 'sandbox'

# create Postmen API handler object

api = Postmen(api_key, region)

def order_type(order):

    order_number = ''

    if order.sell_sneakers == True:
        order_number = 'MRR' + order.order_number[1:]

    if order.consign_sneakers == True:
        order_number = 'MRC' + order.order_number[1:]

    return order_number




# ------------------------------------------------------------------------------------------------------------------- #



def create_FedEx(order,user):
    # Make sure to install requests: pip install requests
    import requests

    accounts = Account.objects.filter(email=user.email)
    account = accounts.first()

    shipping = Shipping.objects.filter(email = user.email)
    shipping = shipping.last()

    import pycountry

    input_countries = [shipping.country]

    countries = {}
    for country in pycountry.countries:
        countries[country.name] = country.alpha_3

    codes = [countries.get(country, 'Unknown code') for country in input_countries]

    country_code = codes[0]



    url = 'https://sandbox-api.postmen.com/v3/labels'

    payload = {
    	  "async": False,
    	  "billing": {
    	    "paid_by": "shipper"
    	  },
    	  "customs": {
    	    "billing": {
    	      "paid_by": "recipient"
    	    },
    	    "purpose": "gift"
    	  },
    	  "return_shipment": False,
    	  "is_document": False,
    	  "file_type": "pdf",
    	  "service_type": "fedex_international_priority",
    	  "paper_size": "4x6",
    	  "shipper_account": {
    	    "id": ""
    	  },
    	  "invoice": {
    	    "date": "2015-06-24",
    	    "number": "INV-00123"
    	  },
    	  "references": [
    	    "P_O_NUMBER:00000",
    	    "12345",
    	    "DEPARTMENT_NUMBER:CS4/NGST/150319"
    	  ],
    	  "shipment": {
    	    "ship_from": {
    	      "country": country_code,
    	      "contact_name": user.first_name + ' ' + user.last_name,
    	      "phone": account.phone_number,
    	      "fax": None,
    	      "email": user.email,
    	      "company_name": None,
    	      "street1": shipping.address1,
    	      "street2": shipping.address2,
    	      "street3": shipping.address3,
    	      "city": shipping.city,
    	      "state": shipping.state,
    	      "postal_code": shipping.postcode,
    	      "type": "business",
    	      "tax_id": None
    	    },
    	    "ship_to": {
    	      "contact_name": "MRSNEAKER",
    	      "phone": "07704227926",
    	      "fax": None,
    	      "email": "testemail@gmail.com",
    	      "company_name": "MR SNEAKER LTD",
    	      "street1": "410 BETHNAL GREEN ROAD",
    	      "city": "LONDON",
    	      "postal_code": "E20DJ",
    	      "state": "GREATER LONDON",
    	      "country": "GBR",
    	      "type": "business"
    	    },
    	    "parcels": [
    	      {
    	        "description": "SHOES",
    	        "box_type": "custom",
    	        "weight": {
    	          "value": 2,
    	          "unit": "kg"
    	        },
    	        "dimension": {
    	          "width": 30,
    	          "height": 20,
    	          "depth": 10,
    	          "unit": "cm"
    	        },
    	        "items": [
    	          {
    	            "description": "SHOES",
    	            "origin_country": country_code,
    	            "quantity": 1,
    	            "price": {
    	              "amount": float(order.price),
    	              "currency": "USD"
    	            },
    	            "weight": {
    	              "value": 1.5,
    	              "unit": "kg"
    	            },
    	            "sku": order.product_code
    	          }
    	        ]
    	      }
    	    ]
    	  }
    	}


    payload = json.dumps(payload)
    print(payload)


    headers = {
        'postmen-api-key': api_key,
        'content-type': 'application/json'
    }

    response = requests.request('POST', url, data=payload, headers=headers)

    print(response.text)

    content = json.loads(response.content)
    url = content.get('data').get('files').get('label').get('url')

    order.shipping_label = url
    order.tracking_number = content.get('data').get('tracking_numbers')[0]
    print(order.tracking_number)

    order.save()

    order_number = order_type(order)

    from django.core import mail
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    subject = 'Mrsneaker Shipping Label - ' + str(order_number)
    html_message = render_to_string('shipping_email.html',{'order_number': order_number, 'carrier': 'FedEx', 'url': url, 'tracking_number': order.tracking_number, 'title':order.product_name,'image':order.image})
    plain_message = strip_tags(html_message)
    from_email = 'From <from@example.com>'
    to = user.email

    mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)


def create_DPD(order,user):
    import requests
    import json

    import requests
    import json

    accounts = Account.objects.filter(email=user.email)
    account = accounts.first()

    shipping = Shipping.objects.filter(email=user.email)
    shipping = shipping.last()

    print(vars(shipping))

    import pycountry

    input_countries = [shipping.country]

    countries = {}
    for country in pycountry.countries:
        countries[country.name] = country.alpha_3

    codes = [countries.get(country, 'Unknown code') for country in input_countries]

    country_code = codes[0]

    url = "https://production.courierapi.co.uk/api/couriers/v1/DPDLocal/create-label"

    from datetime import datetime, timedelta
    today = datetime.today()
    collection_date = today + timedelta(days=2)
    collection_date = collection_date.strftime('%Y-%m-%d')

    payload = json.dumps({
        "testing": True,
        "auth_company": "mrsneaker",
        "shipment": {
            "label_size": "4x6",
            "label_format": "pdf",
            "generate_invoice": False,
            "generate_packing_slip": False,
            "courier": {
                "global_product_code": "U",
                "local_product_code": "U",
                "friendly_service_name": "DPDLocal",
                "network_code": "2^68"
            },
            "extra_details": {
                "channel_order_id": 22
            },
            "collection_date": collection_date,
            "reference": "my reference",
            "reference_2": "my second reference",
            "delivery_instructions": "Leave on the porch",
            "shipping_charge": 2.42,
            "ship_from": {
                "name": user.first_name + ' ' + user.last_name,
                "phone": None,
                "email": user.email,
                "company_name": None,
                "address_1": shipping.address1,
                "address_2": shipping.address2,
                "address_3": shipping.address3,
                "city": shipping.city,
                "postcode": shipping.postcode,
                "county": shipping.state,
                "country_iso": "GB",
                "company_id": None,
                "tax_id": None,
                "eori_id": None,
                "ioss_number": None
            },
            "ship_to": {
                "name": "MRSNEAKER",
                "phone": "466546346546",
                "email": "support@buyer.com",
                "company_name": "MRSNEAKER",
                "address_1": "MRSNEAKER LTD",
                "address_2": "410 BETHNAL GREEN ROAD",
                "address_3": None,
                "city": "London",
                "county": "London",
                "postcode": "E20DJ",
                "country_iso": "GB"
            },
            "parcels": [
                {
                    "dim_width": 30,
                    "dim_height": 20,
                    "dim_length": 10,
                    "dim_unit": "cm",
                    "items": [
                        {
                            "description": "SHOES",
                            "origin_country": "GB",
                            "quantity": 1,
                            "value": order.price,
                            "value_currency": "GBP",
                            "weight": 1,
                            "weight_unit": "kg",
                            "sku": order.product_code,
                            "hs_code": "12345"
                        }
                    ]
                }
            ]
        },
        "format_address_default": True,
        "request_id": 123456789
    })
    headers = {
        'api-user': 'mrsneaker',
        'api-token': '',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    print(response.text)

    content = json.loads(response.content)
    tracking_number = content.get('tracking_codes')[0]
    url = content.get('uri')


    order.shipping_label = url
    order.tracking_number = tracking_number

    order.save()


    order_number = order_type(order)

    from django.core import mail
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    subject = 'Mrsneaker Shipping Label - ' + str(order_number)
    html_message = render_to_string('shipping_email.html',{'order_number': order_number, 'carrier': 'DPD', 'url': url, 'tracking_number': order.tracking_number, 'title':order.product_name,'image':order.image})

    plain_message = strip_tags(html_message)
    from_email = 'From <from@example.com>'
    to = user.email

    mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)


