"""Context Processor."""

from django.conf import settings


def google_analytics(request):
    """
    Google Analytics.

    Use the variables returned in this function to
    render your Google Analytics tracking code template.
    """
    ga_prop_id = getattr(settings, 'GOOGLE_ANALYTICS_PROPERTY_ID', False)
    ga_domain = getattr(settings, 'GOOGLE_ANALYTICS_DOMAIN', False)
    if not settings.DEBUG and ga_prop_id and ga_domain:
        return {
            'GOOGLE_ANALYTICS_PROPERTY_ID': ga_prop_id,
            'GOOGLE_ANALYTICS_DOMAIN': ga_domain,
        }
    return {}

def check_login(request):
    if request.user.is_authenticated():
        log_inf = ['Profile','Logout']
        log_link = ['homepage:profile','homepage:logout']
    else:
        log_inf = ['Register','Login']
        log_link = ['homepage:register','login']
    return {'log_inf': log_inf,
            'log_link':log_link
            }

def site(request):
    """Available in all templates."""
    return {
        'domain': settings.CURRENT_DOMAIN,
        'name': settings.CURRENT_NAME,
        'slogan' : settings.CURRENT_SLOGAN,
        }
