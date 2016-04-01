from django.conf.urls import patterns, url
from haystack.query import SearchQuerySet
from haystack.views import search_view_factory

from journal.models import ProfileDetails
from mailing import views
from mailing.models import SubscriberSearchForm, CollectionSearchForm, EmailList
from mailing.views import SubscriberProtectedView, CollectionProtectedView


sqs = SearchQuerySet().models(ProfileDetails)
sqs2 = SearchQuerySet().models(EmailList)
urlpatterns = patterns('',
                       # ex: /polls/
                      url(r'^upload/$', views.upload_file, name='upload'),
                      url(r'^emaillisting/$',views.mail_listing, name='emaillisting'),
                      url(r'^getemailids/$',views.get_email, name="success"),
                      url(r'^journaltemplates/$',views.template_create, name="journaltemplates"),
                      url(r'^journaltemplates/update/(?P<jid>\d+)/$',views.template_update, name= "journaltemplateupdate"),
                      url(r'^journaltemplates/view/(?P<jid>\d+)/$',views.template_view, name="journaltemplateview"),
                      url(r'^unsubscribe$',views.unsubscribe, name="unsubscribe"),
                      url(r'^ebemaillisting/(?P<jid>\d+)/$',views.ebmemberslistings, name='ebemaillisting'),
                      url(r'^eblist/$',views.ajax_eblistings, name='eblist'),
                      url(r'^email/$', views.query_form, name="email"),
                      url(r'^getemailids2/$',views.get_email2, name = "success2"),
                      url(r'^getemailsubscriber/$',views.get_email_subscriber, name="subscribersuccess"),
                      url(r'^subscriber/$',search_view_factory(
                                      view_class=SubscriberProtectedView,                         
                                      template = 'mailing/subscribersearch.html',
                                      searchqueryset=sqs,
                                      results_per_page = 500,
                                      form_class= SubscriberSearchForm) , name='subscriber_search'),
                       url(r'^collection/$',search_view_factory(
                                      view_class=CollectionProtectedView,                         
                                      template = 'mailing/collectionsearch.html',
                                      searchqueryset=sqs2,
                                      results_per_page = 500,
                                      form_class= CollectionSearchForm) , name='collection_search'),
                       )