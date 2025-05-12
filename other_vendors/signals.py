# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from userapp.models import Profile
# from django.conf import settings


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_profile(sender, instance, created, **kwargs):
#     if created and instance.is_active==True:
#         Profile.objects.create(user=instance)

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def save_profile(sender, instance, **kwargs):
#     instance.profile.save()
    
    

