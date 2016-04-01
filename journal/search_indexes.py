import datetime
from haystack import indexes
from journal.models import PublishedManuscript

class PublishedManuscriptIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    abstract = indexes.CharField(model_attr='abstract')
    article = indexes.CharField(model_attr='article')
    create_time = indexes.DateTimeField(model_attr='create_time')
    journal = indexes.CharField(model_attr='journal')

    def get_model(self):
        return PublishedManuscript

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(create_time__lte=datetime.datetime.now())
