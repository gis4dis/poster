from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress


@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):

    user.is_active = False
    user.is_staff = False
    user.save()
