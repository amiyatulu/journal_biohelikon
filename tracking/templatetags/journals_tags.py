from django import template
from django.core.exceptions import ObjectDoesNotExist

from journal.models import PublishedManuscript, ProfileDetails
from tracking.models import Points, InboxCount


register = template.Library()

@register.assignment_tag
def pubmanuscriptall():
    return PublishedManuscript.objects.all().order_by('-create_time')[:10]

@register.filter
def checkforprofile(user):
    profile = ProfileDetails.objects.filter(user = user)
    if profile:
        return True
    else:
        return False
    
@register.filter
def myscore(user):
    try:
        mymarks = Points.objects.get(user=user)
        return mymarks.score
    except ObjectDoesNotExist:
        return 0

@register.filter
def mywallet(user):
    try:
        mymarks = Points.objects.get(user=user)
        return mymarks.ewallet
    except ObjectDoesNotExist:
        return 0

@register.filter
def inboxnumber(user):
    try:
        number = InboxCount.objects.get(user=user)
        return number.count
    except ObjectDoesNotExist:
        return 0        
    