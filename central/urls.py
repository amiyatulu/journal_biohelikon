from django.conf.urls import patterns, url, include
from django.contrib import admin
from haystack.views import SearchView

import journal
from journal.models import DateRangeSearchForm
import tracking


# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'central.views.home', name='home'),
    # url(r'^central/', include('central.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^mailing/', include('mailing.urls',namespace="mailing")),
    url(r'^tracking/', include('tracking.urls', namespace="tracking")),
    url(r'^subjects/', include('journal.urls', namespace="journal")),
    url(r'^journal/article/(?P<aid>\d+)/(?P<slug2>[-\w\d]+)/(?P<slug>[-\w\d]+)/$', journal.views.articlefulldetails, name="fullarticle"),
    url(r'^journal/article/(?P<aid>\d+)/$', journal.views.articlefulldetails, name="fullarticle"),
    url(r'^journal/year/(?P<year>\d+)/$', journal.views.archive, name="articlebyyear"),
    url(r'^journal/issue/(?P<volume>\d+)/(?P<issue>\d+)/$', journal.views.issue, name="issue"),
    url(r'^journal/archive/$', journal.views.issuearchive, name="issuearchive"),
    url(r'^editorial-board/$', journal.views.totalebmembers, name="totalebmembers"),
    url(r'^searcharticle/',SearchView(
                                      template = 'search/search.html',
                                      form_class= DateRangeSearchForm), name='searcharticle'),
    
    url(r'^$', journal.views.journalhome),
    url(r'^faqs/$',journal.views.faqspage, name = "faqspage"),
   
)
