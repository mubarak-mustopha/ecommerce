from .models import SiteDetail


def site_detail(request):
    return {"site_detail": SiteDetail.objects.first()}
