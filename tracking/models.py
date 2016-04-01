from __future__ import division

import datetime
from decimal import Decimal
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail.message import EmailMessage
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver
from django.forms.fields import CharField
from django.forms.models import ModelForm, ModelChoiceField
from django.utils.timezone import utc
import os
import uuid
from captcha.fields import ReCaptchaField



captcha = ReCaptchaField(
    public_key='6LfsbQkTAAAAABGXK3a86JLkodCeMgfr052u0VpW',
    private_key='6LfsbQkTAAAAADDlPY-ssxF1Dlva0-9wrIL1OG6X',
    use_ssl=True
)
class RegistrationForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(), label="Repeat your password", required=True)
    email = CharField(required=True)
    username = CharField(required=True)
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    
    address = CharField(widget=forms.Textarea, required=True)
    research_interest_keywords = CharField(widget=forms.Textarea, required=True)
    captcha= ReCaptchaField(error_messages={'required':'Please try the Captcha'})
    def clean_password(self):
        if self.data['password'] != self.data['password2']:
            raise forms.ValidationError('Passwords are not the same')
        return self.data['password']
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).count():
            raise forms.ValidationError("Email id already exists")
        return email
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).count():
            raise forms.ValidationError("Username already exists")
        return username
    def clean(self,*args, **kwargs):
        self.clean_email()
        self.clean_password()
        self.clean_username()
        return super(RegistrationForm, self).clean(*args, **kwargs)

def clean_unique(form, field, exclude_initial=True, 
                 format="The %(field)s %(value)s has already been taken."):
    value = form.cleaned_data.get(field)
    if value:
        qs = form._meta.model._default_manager.filter(**{field:value})
        if exclude_initial and form.initial:
            initial_value = form.initial.get(field)
            qs = qs.exclude(**{field:initial_value})
        if qs.count() > 0:
            raise forms.ValidationError(format % {'field':field, 'value':value})
    return value

class Journals(models.Model):
    short_name = models.CharField(max_length=128 ,unique = True)
    name = models.CharField(max_length= 500)
    issn = models.CharField(max_length=128, null = True, blank = True)
    def __unicode__(self):
        return self.name



class Manuscript(models.Model):
    journal = models.ForeignKey(Journals)
    title = models.CharField(max_length=500)
    authors = models.TextField()
    authors_affiliation = models.TextField()
    corresponding_author_name = models.TextField()
    corresponding_author_email = models.EmailField(max_length=254)
    corresponding_author_address = models.TextField()
    city = models.CharField(max_length=500)
    country = models.CharField(max_length=500)
    abstract = models.TextField()
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()
    user = models.ForeignKey(User)
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if self.create_time == None:
            self.create_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.update_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(Manuscript, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.title
    
class ManuscriptForm(ModelForm):
    journal = ModelChoiceField(Journals.objects.all(), empty_label= "Select Journal")
    class Meta:
        model = Manuscript
        exclude = ['create_time','update_time','user']

class UserEmailModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.email
class ManuscriptAdminForm(ModelForm):
    journal = ModelChoiceField(Journals.objects.all(), empty_label= "Select Journal")
    user = UserEmailModelChoiceField(User.objects.all())
    class Meta:
        model = Manuscript
        exclude = ['create_time','update_time']

def get_upload_path(instance, filename):
    return os.path.join(
      "user_%d" % instance.user.id, "manuscript_%s" % instance.manuscript.id,"revision_%d" % instance.revision, uuid.uuid4().hex, filename)
        
class JournalsForm(ModelForm):
    class Meta:
        model = Journals
        fields = '__all__'
    
class UploadFile(models.Model):
    files = models.FileField(upload_to= get_upload_path,max_length=10000)
    manuscript = models.ForeignKey(Manuscript)
    user = models.ForeignKey(User)
    revision = models.IntegerField()
    create_time = models.DateTimeField()
    def clean(self):
        acceptedfile = self.files
        if acceptedfile.size > 30*1024*1024:
            raise ValidationError("You have uploaded a file larger than 30Mb")
        extension = os.path.splitext(acceptedfile.name)[1]
        if extension.lower() not in ['.rtf','.zip','.docx','.doc','.ppt','.pptx','.pdf','.xlsx','.xls','.jpg','.jpeg','.gif','.svg','.png','.tif','.tiff','.txt','.mm']:
            raise ValidationError("Only rtf zip docx,doc,ppt,pptx,pdf,xlsx,xls,jpg,jpeg,gif,svg,png,tif,tiff file formats are allowed")
    def filename(self):
        return os.path.basename(self.files.name)
    def __unicode__(self):
        return self.manuscript.title

class Reviewer(models.Model):
    manuscript = models.ForeignKey(Manuscript)
    user = models.ForeignKey(User)
    create_time =models.DateTimeField()
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        self.create_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(Reviewer, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.manuscript.title

class Review(models.Model):
    manuscript = models.ForeignKey(Manuscript)
    user = models.ForeignKey(User)
    title = models.TextField()
    originality = models.TextField()
    typo_errors = models.TextField()
    deepness = models.TextField()
    comprehensible = models.TextField()
    overall_comments = models.TextField()
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if self.create_time == None:
            self.create_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.update_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(Review, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.manuscript.title

class ReviewComment(models.Model):
    review = models.ForeignKey(Review)
    user = models.ForeignKey(User)
    comment = models.TextField()
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if self.create_time == None:
            self.create_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.update_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(ReviewComment, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.review.manuscript.title
    

class ReviewForm(ModelForm):  
    class Meta:
        model = Review
        exclude = ['manuscript','user','create_time','update_time']

def get_upload_path_review(instance, filename):
    return os.path.join(
      "review", "user_%d" % instance.user.id, "manuscript_%s" % instance.manuscript.id, uuid.uuid4().hex, filename)

class UploadReview(models.Model):
    reviewfile = models.FileField(upload_to= get_upload_path_review,max_length=10000)
    manuscript = models.ForeignKey(Manuscript)
    user = models.ForeignKey(User)
    create_time = models.DateTimeField()
    def clean(self):
        acceptedfile = self.reviewfile
        if acceptedfile.size > 30*1024*1024:
            raise ValidationError("You have uploaded a file larger than 30Mb")
        extension = os.path.splitext(acceptedfile.name)[1]
        if extension.lower() not in ['.docx','.doc','.ppt','.pptx','.pdf','.xlsx','.xls','.jpg','.jpeg','.gif','.svg','.png','.tif','.tiff','.txt','.mm']:
            raise ValidationError("Only docx,doc,ppt,pptx,pdf,xlsx,xls,jpg,jpeg,gif,svg,png,tif,tiff file formats are allowed")
    def filename(self):
        return os.path.basename(self.reviewfile.name)
    def __unicode__(self):
        return self.manuscript.title

class ManuscriptComment(models.Model):
    manuscript = models.ForeignKey(Manuscript)
    user = models.ForeignKey(User)
    comment = models.TextField()
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if self.create_time == None:
            self.create_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.update_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(ManuscriptComment, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.manuscript.title
    
    
class ManuscriptAccessCode(models.Model):
    manuscript = models.OneToOneField(Manuscript, primary_key=True)
    accesscode = models.CharField(max_length=255, unique=True) 
    def save(self, *args, **kwargs):
        '''On save, save accesscode'''
        self.accesscode = uuid.uuid4().hex
        super(ManuscriptAccessCode, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.manuscript.title 

class UploadedManuscriptVisibility(models.Model):
    journal = models.ForeignKey(Journals)
    user = models.ForeignKey(User)
    def __unicode__(self):
        return self.user.username
       

class AccessCodeForm(forms.Form):
    accesscode = CharField(required = True)

class ManuscriptStatus(models.Model):
    manuscript = models.OneToOneField(Manuscript, primary_key=True)
    MANUSCRIPT_STATUSES = (
              ('RV','Under Review'),
              ('RS','Under Revision'),
              ('HD','Under Hold'),
              ('AC','Accepted'),
              ('RJ','Rejected'),
              ('PB','Published'),
              ('AP','Accepted, Pdf Done'),
              ('WD','Withdrawn')             
                           )
    status = models.CharField(max_length = 3, choices= MANUSCRIPT_STATUSES)
    admin_comment = models.TextField(null=True,blank=True)
    def __unicode__(self):
        return self.manuscript.title
    

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required= True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    class Meta:
        model = User        
        fields = ['username','first_name','last_name','email']
    def clean_email(self):
        return clean_unique(self,'email')
        

class ChangePassword(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(), label="Repeat your password", required = True)
    def clean_password(self):
        if self.data['password'] != self.data['password2']:
            raise forms.ValidationError('Passwords are not the same')
        return self.data['password']
    
    def clean(self,*args, **kwargs):
        self.clean_password()
        return super(ChangePassword, self).clean(*args, **kwargs)

class EmailDetails(models.Model):
    journal = models.OneToOneField(Journals, primary_key=True)
    email = models.EmailField(max_length=200)
    password = models.CharField(max_length=200)

class ReviewerBuffer(models.Model):
    email = models.EmailField(max_length=200)
    fullname = models.CharField(max_length=200)
    manuscript = models.ForeignKey(Manuscript)
    create_time =models.DateTimeField()
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        self.create_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(ReviewerBuffer, self).save(*args, **kwargs)
    
    class Meta:
        unique_together = (('email','manuscript'),)
    def __unicode__(self):
        return self.email

@receiver(post_save, sender=ReviewerBuffer)
def mail_to_reviewerbuffer(sender,instance, **kwargs):
    '''Send Mail'''
    accesscode = instance.manuscript.manuscriptaccesscode.accesscode
    message = '''Dear Dr. {0} ,<br><br>
        
        You are invited to review the following manuscript.<br>
        <br>
        Title: <b>{1}</b>
        <br><br>
        Abstract: {2}
        <br><br>
        Please use the following access code to get manuscript access
        after registration or login.<br>
        <br><br>
        Website:<br>
        http://www.biohelikon.org<br>
        Link to enter access code:<br>
        http://www.biohelikon.org/tracking/accesscode/<br>
        
        Access Code:<br>
        {3}<br><br>
        <b>You can also share this access code with your colleagues if they want to review.</b><br><br>
        Regards,<br>
        Biohelikon Publishing Group <br>'''.format(instance.fullname.encode('utf-8'), instance.manuscript.title.encode('utf-8'), instance.manuscript.abstract.encode('utf-8'), accesscode)
    subject = 'Invitation for Reviewing Manuscript'
    to_address = instance.email
    from_address = 'Biohelikon<contact@biohelikon.org>'
    msg = EmailMessage(
                           subject, message,from_address,[to_address]
                           )
    msg.content_subtype = "html"
    msg.send()
           

@receiver(post_save, sender=Review)
def mail_to_author_reviewer_on_review(sender,instance,**kwargs):
    if kwargs.get('created', True):
        rv = instance
        mstatus = ManuscriptStatus.objects.get(manuscript = rv.manuscript)
        if mstatus.status == 'RV' or mstatus.status == 'RS':
            try:
                points = Points.objects.get(user = rv.user)
                points.score = points.score + 20
                points.ewallet = points.ewallet + Decimal(20/4).quantize(Decimal('.00'))
            except ObjectDoesNotExist:
                points = Points(user= rv.user, score = 20, ewallet = Decimal(20/4).quantize(Decimal('.00')))
            points.save() 
            message = '''<h4>Thanks for reviewing</h4><p>You have got 20 points for reviewing the manuscript.</p>'''
            notify = Notification(user = rv.user, message = message)
            notify.save()
        queryreviewer = Reviewer.objects.filter(manuscript = instance.manuscript).exclude(user = instance.user)
        userauthor = instance.manuscript.user
        if queryreviewer:
            for reviewer in queryreviewer:
                message = '''Dear Dr. {0} ,<br><br>
                Reviewer has commented on the manuscript:<br>
                <b>{1}</b> <br><br>
                Please login to the tracking system to view the review comment.<br>
                Website:<br>
                http://www.biohelikon.org<br><br>
                Regards,<br>
                Biohelikon Publishing Group<br>'''.format(reviewer.user.first_name.encode('utf-8'),instance.manuscript.title.encode('utf-8'))
                subject = "Review Comments"
                to_address = reviewer.user.email
                from_address = 'Biohelikon<contact@biohelikon.org>'
                msg = EmailMessage(
                                   subject, message, from_address,[to_address]
                                   )
                msg.content_subtype = "html"
                try:
                    msg.send()
                except:
                    pass
                inboxmessage = '''<h4>Reviewer has given comment</h4>
                <p>Reviewer has commented on the manuscript:<br>
                <b>{0}</b></p>'''.format(instance.manuscript.title.encode('utf-8'))
                notify = Notification(user = reviewer.user, message = inboxmessage)
                notify.save() 
        if userauthor:
            message = '''Dear Dr. {0} ,<br><br>
                Reviewer has commented on the manuscript:<br>
                <b>{1}</b> <br><br>
                Please login to the tracking system to view the review comment.<br>
                Website:<br>
                http://www.biohelikon.org<br><br>
                Regards,<br>
                Biohelikon Publishing Group<br>'''.format(userauthor.first_name.encode('utf-8'),instance.manuscript.title.encode('utf-8'))
            subject = "Review Comments"
            to_address = userauthor.email
            from_address = 'Biohelikon<contact@biohelikon.org>'
            msg = EmailMessage(
                                   subject, message, from_address,[to_address]
                                   )
            msg.content_subtype = "html"
            try:
                msg.send()
            except:
                pass
            inboxmessage = '''<h4>Reviewer has given comment</h4>
                <p>Reviewer has commented on the manuscript:<br>
                <b>{0}</b></p>'''.format(instance.manuscript.title.encode('utf-8'))
            notify = Notification(user = userauthor, message = inboxmessage)
            notify.save()

@receiver(post_save, sender=ManuscriptComment)
def mail_to_author(sender,instance,**kwargs):
    userauthor = instance.manuscript.user
    if userauthor.email != instance.user.email:
        message = '''Dear Dr. {0} ,<br><br>
            Reviewer has commented on the manuscript:<br>
            <b>{1}</b> <br><br>
            Please login to the tracking system to view the review comment.<br>
            Website:<br>
            http://www.biohelikon.org<br><br>
            Regards,<br>
            Biohelikon Publishing Group<br>'''.format(userauthor.first_name.encode('utf-8'),instance.manuscript.title.encode('utf-8'))
        subject = "Review Comments"
        to_address = userauthor.email
        from_address = 'Biohelikon<contact@biohelikon.org>'
        msg = EmailMessage(
                               subject, message, from_address,[to_address]
                               )
        msg.content_subtype = "html"
        msg.send()
        

@receiver(post_save, sender=UploadFile)
def mail_to_reviewer_on_revision_submission(sender, **kwargs):
    uploadfile = kwargs.get('instance')
    if uploadfile.revision != 1:
        queryreviewer = Reviewer.objects.filter(manuscript = uploadfile.manuscript)
        for reviewer in queryreviewer:
            message = '''Dear Dr. {0} ,<br><br>
            Author has submitted revised manuscript.<br>
            <b>{1}</b> <br><br>
            Please login to the tracking system to view the revised manuscript.<br>
            Website:<br>
            http://www.biohelikon.org<br><br>
            Regards,<br>
            Biohelikon Team<br>'''.format(reviewer.user.first_name.encode('utf-8'),uploadfile.manuscript.title.encode('utf-8'))
            subject = "Revised Manuscript submitted"
            to_address = reviewer.user.email
            from_address = 'Biohelikon<contact@biohelikon.org>'
            msg = EmailMessage(
                               subject, message, from_address,[to_address]
                               )
            msg.content_subtype = "html"
            try:
                msg.send()
            except:
                pass
            inboxmessage = '''<h4>Revised Manuscript has been submitted</h4>
            <p>Revision has been submitted for manuscript:<br>
            <b>{0}</b></p>'''.format(uploadfile.manuscript.title.encode('utf-8'))
            notify = Notification(user = reviewer.user, message = inboxmessage)
            notify.save()
        
        
           

class ReviewerBufferForm(forms.ModelForm):
    class Meta:
        model = ReviewerBuffer
        exclude = ['manuscript']
        
class Points(models.Model):
    user = models.OneToOneField(User,primary_key=True)
    score = models.BigIntegerField()
    ewallet = models.DecimalField(max_digits = 65, decimal_places=2)
    def __unicode__(self):
        return self.user.username

class UserVoted(models.Model):
    review = models.ForeignKey(Review)
    user = models.ForeignKey(User)

class ReviewPoints(models.Model):
    review = models.OneToOneField(Review,primary_key=True)
    score = models.IntegerField() 

class UserVotedManuscript(models.Model):
    manuscript = models.ForeignKey(Manuscript)
    user = models.ForeignKey(User)

class ManuscriptPoints(models.Model):
    manuscript = models.OneToOneField(Manuscript,primary_key=True)
    score = models.IntegerField() 

class Notification(models.Model):
    user = models.ForeignKey(User)
    message = models.TextField()
    create_time = models.DateTimeField()
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if self.create_time == None:
            self.create_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(Notification, self).save(*args, **kwargs)
     
class InboxCount(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    count = models.IntegerField()

class MailingPreferences(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    review_submission = models.BooleanField(default=True)

    


@receiver(post_save, sender=User) 
def intialScore(sender, **kwargs):
    if kwargs.get('created', True):
        user = kwargs.get('instance')
        points = Points(user= user, score = 10, ewallet=Decimal(10/4).quantize(Decimal('.00')))
        points.save() 
        message = '''<h4>Welcome to Biohelikon</h4><p>You have got 10 points for registering.</p>'''
        notify = Notification(user = user, message = message)
        notify.save()

@receiver(post_save, sender=Notification)
def increaseInboxCount(sender,**kwargs):
    if kwargs.get("created",True):
        notification = kwargs.get('instance')
        try:
            inboxcount = InboxCount.objects.get(user = notification.user)
            inboxcount.count = inboxcount.count + 1
        except ObjectDoesNotExist:
            inboxcount = InboxCount(user = notification.user, count = 1)
        inboxcount.save()

@receiver(post_save, sender=Manuscript)
def scoreManuscriptSubmission(sender, **kwargs):
    if kwargs.get('created', True):
        manu = kwargs.get('instance')
        try:
            points = Points.objects.get(user = manu.user)
            points.score = points.score + 20
            points.ewallet = points.ewallet + Decimal(20/4).quantize(Decimal('.00'))
        except ObjectDoesNotExist:
            points = Points(user= manu.user, score = 20, ewallet= Decimal(20/4).quantize(Decimal('.00')))
        points.save() 
        message = '''<h4>Thanks for Manuscript Submission</h4><p>You have got 20 points for submitting a manuscript.</p>'''
        notify = Notification(user = manu.user, message = message)
        notify.save()
    
@receiver(post_delete, sender=Manuscript)
def deductManuscriptSubmission(sender,**kwargs):
    manu = kwargs.get('instance')
    message = ''' '''
    try:
        points = Points.objects.get(user=manu.user)
        points.score = points.score - 20
        points.ewallet = points.ewallet - Decimal(20/4).quantize(Decimal('.00'))
        message = '''<h4>One of your manuscript has been removed.</h4><p>Your score has been deducted with 20 points because your manuscript has been removed from the tracking system.</p>'''
    except ObjectDoesNotExist:
        points = Points(user = manu.user, score = 0, ewallet = Decimal(0).quantize(Decimal('.00')))
        message = '''<h4>One of your manuscript has been removed.</h4><p>One of your manuscript has been removed from the tracking system.</p>'''
    points.save()
    
    notify = Notification(user = manu.user, message = message)
    notify.save()

@receiver(post_save,sender =ManuscriptStatus )
def deductScorePoints(sender, **kwargs):
    mstatus = kwargs.get('instance')
    if mstatus.status == 'RJ':
        message = '''<h4>One of your manuscript has been rejected.</h4><p>Your score has been deducted with 20 points because your manuscript has been rejected.</p>'''
    if mstatus.status == 'WD':
        message = '''<h4>One of your manuscript has been withdrawn.</h4><p>Your score has been deducted with 20 points because your manuscript has been withdrawn.</p>'''
    if mstatus.status  == 'RJ' or mstatus.status == 'WD':
        try:
            points = Points.objects.get(user = mstatus.manuscript.user)
            points.score = points.score - 20
            points.ewallet = points.ewallet - Decimal(20/4).quantize(Decimal('.00'))
        except ObjectDoesNotExist:
            points = Points(user = mstatus.manuscript.user, score = 0, ewallet = Decimal(0).quantize(Decimal('.00')))
            message = '''<h4>One of your manuscript has been rejected/withdrawn.</h4>'''
        points.save()
        notify = Notification(user = mstatus.manuscript.user, message = message)
        notify.save()
    if mstatus.status == 'PB':
        message = '''<h4>One of your manuscript has been published.</h4><p>You have got 20 points more as your article has been published.</p>'''
        try:
            points = Points.objects.get(user = mstatus.manuscript.user)
            points.score = points.score + 20
            points.ewallet = points.ewallet + Decimal(20/4).quantize(Decimal('.00'))
        except ObjectDoesNotExist:
            points = Points(user= mstatus.manuscript.user, score = 20, ewallet= Decimal(20/4).quantize(Decimal('.00')))
        points.save()
        notify = Notification(user = mstatus.manuscript.user, message = message)
        notify.save()
     
            


def upvoteordownvoteNotify(vote,user):
    if vote == 1:
        message = '''<h4>You have been upvoted</h4><p>You got 10 points for getting an upvote.</p>'''
        notify = Notification(user = user, message = message)
        notify.save()
    if vote == 0:
        message = '''<h4>You have been downvoted</h4><p>You score is deducted with 6 points for getting an downvote.</p>'''
        notify = Notification(user = user, message = message)
        notify.save()


    
        
            
        

    
    