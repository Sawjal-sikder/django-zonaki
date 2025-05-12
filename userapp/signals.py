# from django.db.models.signals import post_save
# from .models import User
# from django.dispatch import receiver
# from .models import Profile


# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#     instance.profile.save()



from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount
from .models import User


@receiver(user_signed_up)
def set_user_role(sender, request=None, user=None, **kwargs):
    if user and SocialAccount.objects.filter(user=user, provider='google').exists():
        print("User signed up with Google")

        if request:
            registration_type = request.session.get('registration_type')

            if registration_type == 'customer':
                user.is_active = True
                user.is_customer = True
                user.is_vendor = False
                user.is_staff = False
                user.is_superuser = False
                user.save()
                print("User role updated: is_customer=True, is_vendor=False, is_active=True")
                
            # elif registration_type == 'vendor':
            #     user.is_vendor = True
            #     user.is_customer = False  
            #     user.is_active = False  # Vendor might be inactive by default
            #     user.save()
            #     print("User role updated: is_vendor=True, is_customer=False, is_active=False")
            else:
                print("Invalid or missing registration type:", registration_type)
        else:
            print("Request object is not available")
    else:
        print("User is not signed up with Google or no SocialAccount exists")
