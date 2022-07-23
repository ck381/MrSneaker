# MrSneaker
This respository contains some examples of code written for the MrSneaker Django web application.

## Available examples
* utilities.py - This contains backend code for customer account registration, login and account authentication.

* hyperwallet.py - This interacts with the hyperwallet API to make automated payments to a customers bank or paypal account.

* international_payments.py - This makes use of the Wise API to perform payout solutions for international customers. Customer details are pulled from the Django database and are used to create and fund a transfer successfully. This transaction is signed for using OpenSSL.

* postman.py - This generates shipping labels for customers using their account details and automatically sends it to their email using a rendered template.

* reports.py - This generates detailed customer reports using data pulled from the SQL database and writes them to an excel file. 

## API's used

* Hyperwallet - https://www.hyperwallet.com/
* Wise - https://wise.com/
* Postmen - https://www.aftership.com/postmen
* Paypal - https://developer.paypal.com/api/rest/
