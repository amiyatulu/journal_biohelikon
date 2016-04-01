from django import template

register = template.Library()

@register.filter
def in_uploadreview(uploads, reviewuserid):
    return uploads.filter(user_id = reviewuserid)
    
