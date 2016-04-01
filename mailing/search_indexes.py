import datetime
from haystack import indexes

from journal.models import ProfileDetails
from mailing.models import EmailList


class CollectionMailIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    email = indexes.CharField(model_attr='email')
    name = indexes.CharField(model_attr='name')
    affiliation = indexes.CharField(model_attr='affiliation')
    subscription = indexes.CharField(model_attr='subscription')
    lastsent = indexes.DateTimeField(model_attr='lastsent', null = True)

    def get_model(self):
        return EmailList

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()


class SubscriberMailIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    user = indexes.CharField(model_attr='user')
    address = indexes.CharField(model_attr='address')
    research_interest = indexes.CharField(model_attr='research_interest')
    education = indexes.CharField(model_attr='education', null = True)
    experience = indexes.CharField(model_attr='experience', null = True)
    publications = indexes.CharField(model_attr='publications', null = True)
    membertype = indexes.CharField(model_attr='membertype')
    journal = indexes.CharField(model_attr='journal', null = True)
    create_time = indexes.DateTimeField(model_attr='create_time')
    update_time = indexes.DateTimeField(model_attr='update_time')

    def get_model(self):
        return ProfileDetails

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(update_time__lte=datetime.datetime.now())
