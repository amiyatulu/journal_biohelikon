from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from haystack.views import SearchView

from mailing.models import UploadFileForm, update_database, handle_uploaded_file, \
    EmailList, JournalTemplatesForm, JournalTemplates, getRandomKey, \
    SendEditorialMail, JTemplate, SendMail2, TemplateSelect, SendMailSubscriber


@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            update_database()
            return HttpResponseRedirect(reverse('mailing:email'))
    else:
        form = UploadFileForm()
    return render(request,'mailing/upload.html',{'form':form,
                                                   })
@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)
def mail_listing(request):
    query = request.GET.get('query')
    dayz = request.GET.get('days')
    journal = request.GET.get('journal')
    journaltemp = JournalTemplates.objects.all()
    
    if query is None and dayz is None and journal is None:
        contact_list = EmailList.objects.filter(subscription = 'Y')
    elif dayz is None and journal is None:
        qry = query.split("_")
        qr = "|".join(qry)
        contact_list = EmailList.objects.filter(affiliation__iregex = qr, subscription = 'Y')
        
    elif query is None and journal is None:
        
        dayz = int(dayz)
        months = datetime.today() - timedelta(days=dayz)
        contact_list = EmailList.objects.filter(Q(lastsent__lte= months)|Q(lastsent__isnull= True))
    elif journal is None:
        dayz = int(dayz)
        months = datetime.today() - timedelta(days=dayz)
        qry = query.split("_")
        qr = "|".join(qry)
        contact_list = EmailList.objects.filter(Q(affiliation__iregex = qr),Q( subscription = 'Y'), Q(lastsent__lte=months) | Q(lastsent__isnull=True))
    else:
        dayz = int(dayz)
        months = datetime.today() - timedelta(days=dayz)
        qry = query.split("_")
        qr = "|".join(qry)
        contact_list = EmailList.objects.filter(Q(affiliation__iregex = qr),Q(affiliation__icontains = journal),Q( subscription = 'Y'), Q(lastsent__lte=months) | Q(lastsent__isnull=True))
        
    paginator = Paginator(contact_list, 500) # Show 25 contacts per page

    page = request.GET.get('page',1)
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)

    return render(request, 'mailing/listing.html', {"contacts": contacts, 'journaltemp':journaltemp})

@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)
def get_email(request):
    if request.method == 'POST':
        ids = request.POST.getlist('Email')
        tempid = request.POST.get('journalid')
        temptype = request.POST.get('templatetype')
        
        return render(request,'mailing/success.html',{'ids':ids,'tempid':tempid,
                                                      'temptype':temptype,
                                                      })
@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)    
def template_create(request):
    if request.method == 'POST':
        form = JournalTemplatesForm(request.POST)
        if form.is_valid():
            f = form.save()
            return HttpResponseRedirect(reverse('mailing:journaltemplateview',args=(f.journal_id,)) )
    else:
        form = JournalTemplatesForm()
    return render(request,'mailing/journaltemplates.html',{'form':form,})

@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)
def template_update(request, jid):
    instance = get_object_or_404(JournalTemplates, journal_id=jid)
    form = JournalTemplatesForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('mailing:journaltemplateview',args=(jid,)) )
    return render(request, 'mailing/journaltemplatesupdate.html', {'form': form} )      

@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)
def template_view(request, jid):
    journaltemp = get_object_or_404(JournalTemplates,journal_id=jid)
    return render(request, 'mailing/journaltemplateview.html',{'journaltemp':journaltemp}) 

def unsubscribe(request):
    mail = request.GET.get('email')
    key = request.GET.get('key') 
    if mail is None or key is None:
        return render(request,'mailing/pagenotfound.html')
    else:
        e = EmailList.objects.get(email = mail)
        if e.subscriptionkey == key :
            e.subscription = 'N'
            e.subscriptionkey = getRandomKey()
            e.save()
            return render(request,'mailing/unsubscribesuccess.html')
        else:
            return render(request,'mailing/pagenotfound.html')

@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)
def ebmemberslistings(request, jid):
    jid = int(jid)
    contact_list = User.objects.filter(profiledetails__journal__id = jid, profiledetails__membertype = 'eb')
    return render(request, 'mailing/eblisting.html', {"contacts_list": contact_list})    

@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)
def ajax_eblistings(request):  
    if request.method == 'POST':
        ids = request.POST.getlist('Email')
        tempid = request.POST.get('journalid')
        s = SendEditorialMail(ids,tempid)
        status = s.mail()
        
        return render(request,'mailing/success.html',{'ids':ids,'tempid':tempid,'status':status,
                                                      })
    else:
        journaltemp = JournalTemplates.objects.all()
    return render(request,'mailing/ajaxeblisting.html',{'journaltemp':journaltemp})

@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)
def query_form(request):
    query = request.GET.get('query')
    days = request.GET.get('days')
    template = JTemplate.objects.all()
        
    if (query is None or query == "") and ( days is None or days == ""):
        contact_list = EmailList.objects.filter(subscription = 'Y')
    elif days is None or days == "":
        contact_list = EmailList.objects.filter(affiliation__iregex = query, subscription = 'Y')
    elif query is None or query == "":
        days = int(days)
        months = datetime.today() - timedelta(days=days)
        contact_list = EmailList.objects.filter(Q(lastsent__lte= months)|Q(lastsent__isnull= True),Q( subscription = 'Y'))
    else:
        days = int(days)
        months = datetime.today() - timedelta(days=days)
        contact_list = EmailList.objects.filter(Q(affiliation__iregex = query),Q( subscription = 'Y'), Q(lastsent__lte=months) | Q(lastsent__isnull=True))
    
    paginator = Paginator(contact_list, 500) 

    page = request.GET.get('page',1)
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    return render(request, 'mailing/querylisting.html', {"contacts": contacts,"template":template,}) 

@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)
def get_email2(request):
    if request.method == 'POST':
        ids = request.POST.getlist('Email')
        tempid = request.POST.get('templatename')
        tid = int(tempid)
        template = get_object_or_404(JTemplate, id = tid)
        
        s = SendMail2(ids,tempid)
        status = s.mail()
        
        return render(request,'mailing/success2.html',{'ids':ids,'template':template,'status':status
                                                      })  
        
@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)
def get_email_subscriber(request):
    if request.method == 'POST':
        ids = request.POST.getlist('Email')
        tempid = request.POST.get('templatename')
        tid = int(tempid)
        template = get_object_or_404(JTemplate, id = tid)
        
        s = SendMailSubscriber(ids,tempid)
        status = s.mail()
        
        return render(request,'mailing/subscribersuccess.html',{'ids':ids,'template':template,'status':status
                                                      })
        
        

class  SubscriberProtectedView(SearchView):
    def __call__(self, request):
        if request.user.is_staff:
            return super(SubscriberProtectedView, self).__call__(request)
        else:
            raise Http404("Page not found") 
    def extra_context(self):
        form2 = TemplateSelect
        return {'form2':form2}
        

class CollectionProtectedView(SearchView):
    def __call__(self, request):
        if request.user.is_staff:
            return super(CollectionProtectedView, self).__call__(request)
        else:
            raise Http404("Page not found") 
    def extra_context(self):
        form2 = TemplateSelect
        return {'form2':form2}
                  
            
    
                
                
                
            
