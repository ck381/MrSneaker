# MrSneaker

These contain some examples of code written for the MrSneaker Django web application.

utilities.py - This contains backend code for customer account registration, login and account authentication.

Hyperwallet.py - This interacts with the hyperwallet API (https://www.hyperwallet.com/) to make automated payments to a customers bank / paypal account.

international_payments.py - This makes use of the Wise API (https://wise.com/) to perform payout solutions for international customers. Customer details are pulled from the Django database and are used to create and fund a transfer successfully. This transaction is signed for using OpenSSL.

postman.py - This generates shipping labels for customers using their details and automatically sends it to their email using a rendered template.

reports.py - This generates detailed customer reports using data pulled from the SQL database and writes them to an excel file. 
