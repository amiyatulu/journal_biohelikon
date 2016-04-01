from PIL import Image
import datetime
from django import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.forms.models import ModelForm, ModelChoiceField
from django.template.defaultfilters import slugify
from django.utils.timezone import utc
from haystack.forms import SearchForm
from os import path
import os

from central.settings import MEDIA_ROOT
from tracking.models import Journals, Manuscript


def get_upload_path_user(instance, filename):
    return os.path.join(
       "profileimages","profileuser_%d" % instance.user.id, filename)


MEMBER_TYPE = (
            ('eb','Eb Member'),
            ('rv','Reviewer'),
            ('sub','Subscriber')
                   )       
class ProfileDetails(models.Model):
    user = models.OneToOneField(User,primary_key=True)
    address = models.TextField()
    research_interest = models.TextField()
    education = models.TextField(null=True,blank=True)
    experience = models.TextField(null=True,blank=True)
    publications = models.TextField(null=True,blank=True)
    
    membertype = models.CharField(max_length=100, choices = MEMBER_TYPE)
    journal = models.ForeignKey(Journals, null=True,blank=True)
    arrange = models.CharField(max_length=1000, null=True, blank = True)
    photo = models.ImageField(upload_to=get_upload_path_user,max_length=10000,null=True,blank=True)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if self.create_time == None:
            self.create_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.update_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        if not self.membertype:
            self.membertype ='sub'
        super(ProfileDetails, self).save(*args, **kwargs)
        if self.photo.name:
            filename = MEDIA_ROOT + self.photo.name
            size = (300,300)
            image = Image.open(filename)
            image.thumbnail(size,Image.ANTIALIAS)
            image.save(filename)
    def __unicode__(self):
        return self.user.username + " " + self.user.first_name + " " + self.user.last_name + " " + self.user.email
class PublishedManuscript(models.Model):
    title = models.TextField()
    abstract = models.TextField()
    authors = models.TextField(null = True,blank=True)
    metatag = models.TextField(null = True, blank=True)
    article = models.TextField()
    volume = models.CharField(max_length=1000)
    issue = models.CharField(max_length=20)
    year = models.CharField(max_length=4)
    e_locator = models.CharField(max_length=1000)
    link = models.CharField(max_length=1000)
    supp_link = models.TextField(null=True,blank=True)
    size = models.CharField(max_length=1000)
    journal = models.ForeignKey(Journals)
    manuscript = models.OneToOneField(Manuscript, null=True, blank=True)
    REVISION_TYPES = (
              ('Major','Major'),
              ('Minor','Minor'),             
                           )
    revisiontype = models.CharField(max_length=10, choices= REVISION_TYPES)
    slug = models.SlugField()
    slug2 = models.SlugField()
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if self.create_time == None:
            self.create_time = datetime.datetime.utcnow().replace(tzinfo=utc)
            self.revisiontype = 'Major'
        self.update_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.slug = slugify(self.title)
        self.slug2 = slugify("biohelikon-"+ self.e_locator)
        super(PublishedManuscript, self).save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse('journal.views.articlefulldetails', kwargs={'aid': str(self.id),'slug2': str(self.slug2),'slug':str(self.slug)})
    def __unicode__(self):
        return self.title

class PublishedManuscriptRevisions(models.Model):
    publishedmanuscript = models.ForeignKey(PublishedManuscript)
    title = models.TextField()
    abstract = models.TextField()
    authors = models.TextField(null = True, blank=True)
    metatag = models.TextField(null = True, blank=True)
    article = models.TextField()
    volume = models.CharField(max_length=1000)
    issue = models.CharField(max_length=20)
    year = models.CharField(max_length=4)
    e_locator = models.CharField(max_length=1000)
    link = models.CharField(max_length=1000)
    supp_link = models.TextField(null=True,blank=True)
    size = models.CharField(max_length=1000)
    version = models.CharField(max_length=1000)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if self.create_time == None:
            self.create_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.update_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(PublishedManuscriptRevisions, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.title

class JournalLink(models.Model):
    journals = models.OneToOneField(Journals)
    home = models.CharField(max_length=250, unique = True)
    def __unicode__(self):
        return self.journals.name
    


def get_upload_path_homephoto(instance, filename):
    return os.path.join(
       "homephoto","homephotoid_%d" % instance.journals.id, filename)



class JournalHome(models.Model):
    journals = models.OneToOneField(Journals)
    h1 = models.CharField(max_length=500)
    block1 = models.TextField()
    block2 = models.TextField(null = True, blank =True ,verbose_name= "metatag")
    block3 = models.TextField(null=True, blank=True)
    block4 = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to=get_upload_path_homephoto,max_length=10000)
    def __unicode__(self):
        return self.journals.name

class Instructions(models.Model):
    journals = models.OneToOneField(Journals)
    block1 = models.TextField()
    block2 = models.TextField(null = True, blank =True)
    block3 = models.TextField(null=True, blank=True)
    def __unicode__(self):
        return self.journals.name
    
class AboutJournal(models.Model):
    journals = models.OneToOneField(Journals)
    block1 = models.TextField()
    block2 = models.TextField(null = True, blank =True)
    block3 = models.TextField(null=True, blank=True)
    def __unicode__(self):
        return self.journals.name
    
    
     
    

class ProfileDetailsForm(ModelForm):
    class Meta:
        model = ProfileDetails
        exclude = ['create_time','update_time']

class ProfileDetailsUserForm(ModelForm):
    class Meta:
        model = ProfileDetails
        exclude = ['create_time','update_time','user','membertype','journal','arrange']

class FormatString(str):
    def format(self, *args, **kwargs):
        arguments = list(args)
        arguments[1] = path.basename(arguments[1])
        return super(FormatString, self).format(*arguments, **kwargs)


class SmallClearableFileInput(forms.ClearableFileInput):
    url_markup_template = FormatString('<a href="{0}">{1}</a>')

class ProfileDetailsUserUpdateForm(ModelForm):
    class Meta:
        model = ProfileDetails
        exclude = ['create_time','update_time','user','membertype','journal','arrange']
        widgets = {'photo':  SmallClearableFileInput}
        
class PublishedManuscriptForm(ModelForm):
    class Meta:
        model = PublishedManuscript
        exclude=['create_time','update_time','revisiontype','slug','slug2']

class PublishedManuscriptUpdateForm(ModelForm):
    class Meta:
        model = PublishedManuscript
        exclude=['create_time','update_time','slug','slug2']

@receiver(post_save, sender=PublishedManuscript)
def copy_revisions(sender,instance, **kwargs):
    if instance.revisiontype == "Major":
        count = PublishedManuscriptRevisions.objects.filter(publishedmanuscript_id = instance.id).count()
        version = count + 1
        p = PublishedManuscriptRevisions(publishedmanuscript_id = instance.id, title = instance.title,authors= instance.authors, metatag = instance.metatag, abstract = instance.abstract,
                                     article = instance.article, volume = instance.volume, issue = instance.issue ,year = instance.year, e_locator = instance.e_locator,
                                     link = instance.link,supp_link = instance.supp_link, size = instance.size, version = version
                                     )
        p.save()
    else:
        try:
            rev = PublishedManuscriptRevisions.objects.filter(publishedmanuscript_id = instance.id).order_by('-id')[0]
            rev.title = instance.title
            rev.abstract = instance.abstract
            rev.authors = instance.authors
            rev.metatag = instance.metatag
            rev.article = instance.article
            rev.volume = instance.volume
            rev.issue = instance.issue
            rev.year = instance.year
            rev.e_locator = instance.e_locator
            rev.link = instance.link
            rev.supp_link = instance.supp_link
            rev.size = instance.size
            rev.save()
        except:
            pass




class DateRangeSearchForm(SearchForm):
    models = [
        PublishedManuscript
    ]

    
    journal = ModelChoiceField(queryset=Journals.objects.all(),required=False,empty_label= "All", label="Subjects")
    def get_models(self):
        return self.models
    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(DateRangeSearchForm, self).search().models(*self.get_models())

        if not self.is_valid():
            return self.no_query_found()

        # Check to see if a start_date was chosen.
        if self.cleaned_data['journal']:
            sqs = sqs.filter(journal=self.cleaned_data['journal'])


        # Check to see if an end_date was chosen.
        

        return sqs

            
        
    
        
    
