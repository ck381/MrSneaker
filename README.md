# MrSneaker

<p align="center">
  <img src=https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRel4E8Un_wh64A7l13SHl_lYI-pbVNx3wJEw&usqp=CAU" width="350" title="Binance Smart Chain">
</p>


This respository contains some examples of code written for the MrSneaker Django web application.

<b>utilities.py</b> - This contains backend code for customer account registration, login and account authentication.

<b>hyperwallet.py</b> - This interacts with the hyperwallet API to make automated payments to a customers bank or paypal account.

<b>international_payments.py</b> - This makes use of the Wise API to perform payout solutions for international customers. Customer details are pulled from the Django database and are used to create and fund a transfer successfully. This transaction is signed for using OpenSSL.

<b>postman.py</b> - This generates shipping labels for customers using their account details and automatically sends it to their email using a rendered template.

<b>reports.py</b> - This generates detailed customer reports using data pulled from the SQL database and writes them to an excel file. 
