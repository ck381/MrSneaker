
# Creates a new customers account
def register(request):

    from django.contrib.auth import get_user_model
    from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
    from django.contrib.sites.shortcuts import get_current_site

    from django.core.mail import send_mail

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        data = form.data

        email = form.data.get('email')
        password = form.data.get('password')
        firstName = form.data.get('first_name')
        lastName = form.data.get('last_name')
        name = form.data.get('name')
        phone_number = form.data.get('phoneNum')

        try:

            user = User.objects.create_user(username = email, email = email, password = password)
            user.first_name = firstName
            user.last_name = lastName

            account = Account(account_ID = email, email = email, phone_number = phone_number, city = '', street = '', country = '', post_code = '', state = '', paypal_email = '')
            account.save()

            user.is_active = False

            # Generate a random token

            import secrets

            token = secrets.token_hex(6)
            token = token.upper()

            account.token = token
            account.save()

            # Send email

            from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode



            from django.core import mail
            from django.template.loader import render_to_string
            from django.utils.html import strip_tags
            from django.utils.encoding import force_bytes, force_str, force_text

            uid = urlsafe_base64_encode(force_bytes(user.pk))

            html_message = render_to_string('register_email.html',{'token': token,'uid':uid})


            to = str(user.email)

            email = Email.objects.first()

            success = send_mail(
            'Registration',
            'message',
            'support@mrsneaker.com',
            [to],
            fail_silently = False,
            html_message = html_message,
            )

            user.save()

            return render(request, "verify-email.html", {'email':user.email})  # Redirect the user to the home page upon successful registration


        except Exception as e:

            print(e)

            return redirect("/register")  # Redirect the user to the home page upon successful registration

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})

# ----------------------------------------------- #


# This functions authenticates and logs a user in
def login(request):

    #context = RequestContext(request)
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        data = form.data
        username = data.get('email')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth_login(request, user)
            if user.is_superuser:
                return redirect("/admin-dashboard/")  # Redirect the user to the home page upon successful registration
            else:
                return redirect("/dashboard/")  # Redirect the user to the home page upon successful registration


        else:
            return redirect("/login")

    else:
        form = RegisterForm()

    return render(request, "login.html", {"form": form})


# ----------------------------------------------- #


from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
account_activation_token = TokenGenerator()
]

# Activate the users account
def activate(request, uidb64, token):
    from django.contrib.auth import get_user_model
    from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None:
        account = Account.objects.filter(email = user.email).last()
        if account.token == token:
            user.is_active = True
            user.save()
            print('here')
            return redirect("/login")
    else:
        print('here1')
        return redirect("/login")

    return redirect("/login")