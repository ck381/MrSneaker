from datetime import datetime, timedelta
import pandas as pd
import time
import json
import requests
import re
from mrsneaker_main.models import Account, Order, Bank, product_reserve, fees, Card, Shipping, open_offer, User
from django.core.paginator import Paginator




import pandas as pd
from styleframe import *


def get_order_price(order):
    price = order.attributes.get('total_price')
    return price

def get_order_time(order):
    time = order.attributes.get('processed_at')[0:10]
    return time

def get_order_sku(order):
    sku = order.attributes.get('line_items')[0].attributes.get('sku')
    return sku

def get_order_size(order):
    order = order.attributes.get('line_items')[0]
    size = order.attributes.get('variant_title')

    print(size)


    final_size = ''
    done = False
    for i in range (0, len(size) - 1):
        if not done:
            if size[i].isdigit():
                final_size = final_size + size[i]
                if size[i+1] == '.':
                    final_size = final_size + size[i+1]
                    final_size = final_size + size[i+2]
                try:
                    if size[i+2].isdigit():
                        final_size = final_size + size[i+1]
                        final_size = final_size + size[i+2]
                        final_size = final_size + size[i+3]
                except:
                    print('String too short')

                if size[i+1].isdigit():
                    final_size = final_size + size[i+1]

                done = True




    return final_size


def order_type(order):

    order_number = ''

    if order.sell_sneakers == True:
        order_number = 'MRR' + order.order_number[1:]

    if order.consign_sneakers == True:
        order_number = 'MRC' + order.order_number[1:]

    return order_number


def mop(order):

    if order.bank:

        return 'Bank'

    if order.cash:

        return 'Cash'

    if order.paypal:

        return 'Paypal'


def average_purchase_price_size(product_code, uk_size, us_size):


    orders = Order.objects.filter(product_code = product_code, UK_size = uk_size)

    import numpy as np

    price = []

    for order in orders:
        price.append(float(order.price))

    return str(round(np.sum(price) / len(orders),2))

def average_purchase_price_shoe(product_code):


    orders = Order.objects.filter(product_code = product_code)

    import numpy as np

    price = []

    for order in orders:
        price.append(float(order.price))

    return str(round(np.sum(price) / len(orders),2))

def total(orders,type):



    type = type.lower()
    if type == 'cash':
        orders = orders.filter(cash = True)
        total = sum([order.price for order in orders])
    if type == 'paypal':
        orders = orders.filter(paypal = True)
        total = sum([order.price for order in orders])
    if type == 'cash':
        orders = orders.filter(bank = True)
        total = sum([order.price for order in orders])

    return total




def create_excel_sheet():

    import pandas as pd
    import datetime

    print('MAKING EXCEL SHEET')

    orders = Order.objects.all().order_by('order_number')
    paginator = Paginator(orders, 500)

    item_number = []
    purchase_date = []
    product_code = []
    uk_size = []
    sku = []
    mop_list = []
    price = []
    average_purchase_price_by_size = []
    average_purchase_price_by_shoe = []
    seller_name = []
    seller_address = []
    seller_country = []
    seller_postcode = []
    seller_email = []
    us_size = []
    sku_us = []
    received = []
    on_shopify = []
    paid_seller = []
    brand = []
    barcode = []
    style_names = []
    barcode = []



    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        print(page)
        for order in page.object_list:


                shipping = Shipping.objects.filter(email = order.account_ID)
                shipping = shipping.last()



                if shipping != None:

                        try:
                            a = time.perf_counter()


                            account = Account.objects.filter(email = order.account_ID).first()

                            b = time.perf_counter()

                            item_number.append(order_type(order))
                            purchase_date.append(order.created_time.strftime("%Y-%m-%d"))
                            product_code.append(order.product_code)
                            uk_size.append(order.UK_size)
                            sku.append(order.product_code + '-' + order.UK_size)
                            mop_list.append(mop(order))
                            average_purchase_price_by_shoe.append(average_purchase_price_shoe(order.product_code))
                            seller_name.append(account.full_name)
                            seller_address.append(shipping.address1 + ' ' + shipping.address2 + ' ' + shipping.address3)
                            seller_country.append(shipping.country)
                            seller_postcode.append(shipping.postcode)
                            seller_email.append(order.account_ID)
                            us_size.append(order.US_size)
                            received.append(order.received)
                            on_shopify.append(order.on_shopify)
                            paid_seller.append(order.authorized)
                            brand.append(order.brand)
                            sku_us.append(order.product_code + '-' + order.US_size)
                            barcode.append(order.barcode)
                            price.append(order.price)
                            style_names.append(order.product_name)
                            barcode.append(order.barcode)


                        except Exception as e:
                            print(e)




    df1 = pd.DataFrame(list(zip(item_number,purchase_date,product_code,uk_size,sku,price,received,on_shopify,paid_seller,brand,style_names,average_purchase_price_by_shoe, seller_name,seller_address,seller_country,seller_postcode,seller_email,mop_list,barcode)),

        columns=['Item Number', 'Purchase Date', 'Product Code', 'UK Size', 'SKU', 'Purchase Price', 'Received', 'On Shopify','Paid Seller','Brand','Style Name','Average Purchase Price By Shoe', 'Seller Name', 'Seller Address', 'Seller Country', 'Seller Postcode', 'Seller Email','MOP','Barcode'])



    df1.to_excel('reports.xlsx')

    df = pd.read_excel('reports.xlsx')


    df = df.drop(df.columns[0], axis=1)

    df.to_excel('reports.xlsx')

    excel_writer = StyleFrame.ExcelWriter('reports.xlsx')



    sf = StyleFrame(df)

    sf.style_alternate_rows(styles=[Styler(bold=False,
                                             bg_color='#cfe2f3',font_size = 10,font = 'Montserrat'),
                                    Styler(bold=False,
                                             bg_color='#ffffff', font_size = 10,font = 'Montserrat')])

    sf.apply_headers_style(styler_obj=Styler(bold=False,
                                             bg_color='#a4c2f4',font_size = 10, font = 'Montserrat'))


    columns = ['Item Number', 'Purchase Date', 'Product Code', 'UK Size', 'SKU', 'Purchase Price', 'Received', 'On Shopify','Paid Seller','Brand','Style Name','Average Purchase Price By Shoe', 'Seller Name', 'Seller Address', 'Seller Country', 'Seller Postcode', 'Seller Email','MOP','Barcode']
    sf.to_excel(
        excel_writer=excel_writer,
        best_fit=columns,
        row_to_add_filters=0,
    )

    excel_writer.save()


