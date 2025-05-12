from .models import WebsiteInformation

def website_logo(request):
    return {'logo':WebsiteInformation.objects.first()}
