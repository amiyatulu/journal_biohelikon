from __future__ import print_function
from datetime import datetime, timedelta
from django import forms
from django.contrib.auth.models import User
from django.core.mail import get_connection
from django.core.mail.message import EmailMessage
from django.db import models
from django.db.models.query_utils import Q
from django.forms.models import ModelForm
from django.utils.timezone import utc
import hashlib
from haystack.forms import SearchForm
from haystack.inputs import Raw
import os
import random
import re
from smtplib import SMTPAuthenticationError
import time
import traceback

from central import settings
from journal.models import  MEMBER_TYPE
from tracking.models import Journals


class EmailList(models.Model):
    email = models.EmailField(max_length=75, unique=True)
    name = models.CharField(max_length=200)
    affiliation = models.TextField()
    SUBSCRIPTION_CHOICES =(
                           ('Y','Yes'),
                           ('N','NO'),
                           )
    subscription = models.CharField(max_length=2,choices=SUBSCRIPTION_CHOICES)
    subscriptionkey = models.CharField(max_length=1000)
    lastsent = models.DateTimeField(null= True)
    def __unicode__(self):
        return self.email

class UploadFileForm(forms.Form):
    file = forms.FileField() 
    
def handle_uploaded_file(f):
    d = settings.HIDDEN_ROOT + "emailfiles/"
    if not os.path.exists(d):
        os.mkdir(d)
    with open(d +"email.txt",'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
def getRandomKey():
        t1 = time.time()
        t2 = random.getrandbits(128)
        base = hashlib.md5(str(t1 +t2) )
        sid = base.hexdigest()
        return sid

def update_database():
    fh =  open(settings.HIDDEN_ROOT + "emailfiles/email.txt")
    errorfh = open(settings.MEDIA_ROOT + "HsR6WE71a8error.txt", 'w')
    savefh = open(settings.MEDIA_ROOT + "HsR6WE71a8error2.txt", 'w')
    for line in fh:
        ln = line.split("\t")
        key = getRandomKey()
        try:
            e = EmailList(email= ln[0],name = ln[1],affiliation = ln[2],subscriptionkey = key,subscription = 'Y')
            try:
                e.save()
            except Exception as err:
                print(str(err)+ "\n" + line , file = savefh)
        except Exception as err:
            print (str(err) + "\n" + line + "\n", file = errorfh)

class JournalTemplates(models.Model):
    journal = models.OneToOneField(Journals, primary_key=True)
    journal_ebmember_invitation_subject = models.CharField(max_length=500)
    journal_ebmember_invitation = models.TextField()
    journal_callforpapers_subject = models.CharField(max_length=500)
    journal_callforpapers = models.TextField()
    journal_editorial_subject = models.CharField(max_length=500)
    journal_editorial_invitation = models.TextField()
    journal_email = models.EmailField()
    journal_username = models.CharField(max_length=200)
    journal_password = models.CharField(max_length=200)
    def __unicode__(self):
        return self.journal.name

class UserLastSent(models.Model):
    user = models.OneToOneField(User, primary_key = True)
    lastsent = models.DateTimeField(null= True)

class JTemplate(models.Model):
    name = models.CharField(max_length=250, unique=True)
    subject = models.CharField(max_length=250)
    body = models.TextField()
    journal = models.ForeignKey(Journals)
    def __unicode__(self):
        return self.name

class JournalEmailDetails(models.Model):
    journal = models.OneToOneField(Journals, primary_key=True)
    email = models.EmailField()
    username = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    def __unicode__(self):
        return self.journal.name



class JournalTemplatesForm(ModelForm):
    journal_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = JournalTemplates 
        fields = '__all__'
        

#             try:
#                 session.sendmail(from_email,address,msg.as_string())
#                 mailobject.lastsent = datetime.today()
#                 mailobject.save()
#             except SMTPRecipientsRefused:
#                 contact = EmailList.objects.get(email= address)
#                 contact.delete()
#             except UnicodeEncodeError:
#                 contact = EmailList.objects.get(email= address)
#                 contact.delete()
#             except SMTPSenderRefused:
#                 contact = EmailList.objects.get(email= address)
#                 contact.delete()
#             except:
#                 contact = EmailList.objects.get(email= address)
#                 contact.delete()
                
  

    



class SendEditorialMail():
    def __init__(self,x,y): 
        self.mailids = x
        self.tempid = y
    def mail(self):
        tmpid = int(self.tempid)
        temp = JournalTemplates.objects.get(pk = tmpid)
        from_email = temp.journal_email
        my_username = temp.journal_username
        my_password = str(temp.journal_password)
        my_host = "smtp.webfaction.com" 
        connection = get_connection(host=my_host,
                                username= my_username,
                                password= my_password,
                                )
        subject = temp.journal_editorial_subject
        body = temp.journal_editorial_invitation        
        for pid in self.mailids:
            pid = int(pid)
            mailobject = User.objects.get(pk = pid)
            address = mailobject.email            
            bodycontent = re.sub("\[NAME\]",mailobject.get_full_name(),body)
            bdcontent = bodycontent 
            msg = EmailMessage(subject, bdcontent, from_email, [address], connection = connection )
            msg.content_subtype = "html"
            try:
                msg.send()
            except SMTPAuthenticationError:
                return "SMTPAuthenticationError" 
            try:
                usersent = UserLastSent.objects.get(user_id = pid)
            except UserLastSent.DoesNotExist:
                usersent= None
            if usersent:
                usersent.lastsent = datetime.utcnow().replace(tzinfo=utc)
            else:
                UserLastSent.objects.create(user_id = pid, lastsent = datetime.utcnow().replace(tzinfo=utc))
        return "All mails successfully sent"
                
            
                
       
        



class SendMail2():
    def __init__(self,x,y): 
        self.mailids = x
        self.tempid = y
    def mail(self):
        tmpid = int(self.tempid)
        temp = JTemplate.objects.get(pk = tmpid)
        from_email = temp.journal.journalemaildetails.email
        my_username = temp.journal.journalemaildetails.username
        my_password = str(temp.journal.journalemaildetails.password)
        subject = temp.subject
        body = temp.body
        my_host = "smtp.webfaction.com" 
        connection = get_connection(host=my_host,
                                username= my_username,
                                password= my_password,
                                )
        for pid in self.mailids:
            pid = int(pid)
            mailobject = EmailList.objects.get(pk = pid)
            address = mailobject.email            
            bodycontent = re.sub("\[NAME\]",mailobject.name,body)
            bdcontent = bodycontent + "<p><br/><br/>If you don't want to receive  any further mail from Biohelikon, please click on <a href=\"http://www.biohelikon.org/mailing/unsubscribe?email=" + mailobject.email + "&key=" + mailobject.subscriptionkey + "\"> unsubscribe</a>.</p>"
            bdcontent = bdcontent
            msg = EmailMessage(subject, bdcontent, from_email, [address], headers = {'List-Unsubscribe':"<http://www.biohelikon.org/mailing/unsubscribe?email=" + mailobject.email + "&key=" + mailobject.subscriptionkey +">" , 'Precedence': 'bulk'},connection = connection)
            msg.content_subtype = "html"
            try:
                msg.send()
                mailobject.lastsent = datetime.utcnow().replace(tzinfo=utc)
                mailobject.save()
            except SMTPAuthenticationError:
                return "SMTPAuthenticationError"
            except:
                contact = EmailList.objects.get(email= address)
                contact.delete()
        return "Sending all mails successful"
    

class SendMailSubscriber():
    def __init__(self,x,y): 
        self.mailids = x
        self.tempid = y
    def mail(self):
        tmpid = int(self.tempid)
        temp = JTemplate.objects.get(pk = tmpid)
        from_email = temp.journal.journalemaildetails.email
        my_username = temp.journal.journalemaildetails.username
        my_password = str(temp.journal.journalemaildetails.password)
        subject = temp.subject
        body = temp.body
        my_host = "smtp.webfaction.com" 
        connection = get_connection(host=my_host,
                                username= my_username,
                                password= my_password,
                                )
        for pid in self.mailids:
            pid = int(pid)
            mailobject = User.objects.get(pk = pid)
            address = mailobject.email            
            bodycontent = re.sub("\[NAME\]",mailobject.get_full_name(),body)
            bdcontent = bodycontent 
            msg = EmailMessage(subject, bdcontent, from_email, [address], connection = connection)
            msg.content_subtype = "html"
            try:
                msg.send()
                try:
                    sentobject = UserLastSent.objects.get(pk=pid)
                    sentobject.lastsent = datetime.utcnow().replace(tzinfo=utc)
                    sentobject.save() 
                except:
                    sentobject = UserLastSent(user_id = pid, lastsent = datetime.utcnow().replace(tzinfo=utc))
                    sentobject.save()
            except SMTPAuthenticationError:
                return "SMTPAuthenticationError"
        return "Sending all mails successful"


class SubscriberSearchForm(SearchForm):
    MEMBER_TYPES = (("", "All"),)+MEMBER_TYPE
    membertype = forms.ChoiceField( choices = MEMBER_TYPES,required=False, label="Member Type")
    journal = forms.ModelChoiceField(queryset=Journals.objects.all(),required=False,empty_label= "All")
    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(SubscriberSearchForm, self).search()
        
        if not self.is_valid():
            return self.no_query_found()
        
        # Check to see if a start_date was chosen.
        if self.cleaned_data['membertype'] and self.cleaned_data['journal']:
            sqs = sqs.filter(membertype=self.cleaned_data['membertype'], journal = self.cleaned_data['journal'])
        
        elif self.cleaned_data['membertype']:
            sqs = sqs.filter(membertype=self.cleaned_data['membertype'])
        
        elif self.cleaned_data['journal']:
            sqs = sqs.filter(journal=self.cleaned_data['journal'])
        
            
            
        
        return sqs
    

class CollectionSearchForm(SearchForm):
    days = forms.IntegerField(required=False)
    

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(CollectionSearchForm, self).search()
        
        

        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data['days']:
            days = self.cleaned_data['days']
            
            months = datetime.today() - timedelta(days=days)
            sqsa = sqs.filter(Q(lastsent__lte= months),Q( subscription = 'Y'))
            sqsb = sqs.exclude(lastsent = Raw("[* TO *]"))
            sqs = sqsa | sqsb
            
        else:
            sqs= sqs.filter(subscription='Y')
   


        return sqs
    
    
class TemplateSelect(forms.Form):    
    templatename = forms.ModelChoiceField(queryset=JTemplate.objects.all(),required=True, label="Template")


                
        