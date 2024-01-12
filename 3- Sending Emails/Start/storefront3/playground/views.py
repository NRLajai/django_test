from django.shortcuts import render
from django.core.mail import send_mail, mail_admins, BadHeaderError
from sms import send_sms
from templated_mail.mail import BaseEmailMessage

def say_hello(request): 
    try:
        # send_sms('Shopping-verse OTP 123456', '+18573764843', ['+919080257574'], fail_silently=False)
        # send_mail('Testing smtp service', 'Its working? Yes', 'Shopping-verse verification', ['nrlajai28@gmail.com'])
        username = 'lalit'
        email = 'nrlajai28@gmail.com'
        message = BaseEmailMessage(
            template_name='emails/mail.html',
            context={'name': f'{username}'},
        )
        message.send([f'{email}'])
    except BadHeaderError:
        pass
    # return render(request, 'hello.html', {'name': 'Mosh'})
