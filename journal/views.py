from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404

from journal.models import ProfileDetailsForm, PublishedManuscriptForm, \
    PublishedManuscript, PublishedManuscriptUpdateForm, ProfileDetails, \
    ProfileDetailsUserForm, ProfileDetailsUserUpdateForm, JournalLink, JournalHome, \
    Instructions, AboutJournal, DateRangeSearchForm
from tracking.models import Journals


#from rest_framework.renderers import JSONRenderer
# from django.views.decorators.csrf import csrf_exempt
# from tracking.serializers import JournalSerializer
# class JSONResponse(HttpResponse):
#     def __init__(self,data,**kwargs):
#         content = JSONRenderer().render(data)
#         kwargs['content_type']= 'application/json'
#         super(JSONResponse,self).__init__(content,**kwargs)
@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)
def createprofiledetailsadmin(request):
    if request.method =='POST':
        form = ProfileDetailsForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.save()
            return HttpResponseRedirect(reverse('journal:viewprofile',kwargs={'pid':profile.user_id}))
    else:
        form = ProfileDetailsForm()
    return render(request,'journal/createprofiledetails.html',{'form':form,})


@login_required(login_url='/tracking/login2')
def createprofiledetails(request):
    p = ProfileDetails.objects.filter(user = request.user)
    if p:
        return render(request,'tracking/pagenotfound.html')
    else:
        if request.method == 'POST':
            form = ProfileDetailsUserForm(request.POST, request.FILES)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                return HttpResponseRedirect(reverse('journal:viewprofile',kwargs={'pid':profile.user_id}))
        else:
            form = ProfileDetailsUserForm()
        return render(request,'journal/createprofiledetails.html',{'form':form,})
    
@login_required(login_url='/tracking/login2')
def updateprofiledetails(request, pid):
    if request.user.id == int(pid):
        instance = get_object_or_404(ProfileDetails, user_id = pid)
        if request.method == "POST":
            form = ProfileDetailsUserUpdateForm(data= request.POST, files= request.FILES, instance = instance)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('journal:viewprofile',kwargs={'pid':pid}))
        else:
            form = ProfileDetailsUserUpdateForm(instance=instance)
        return render(request,'journal/createprofiledetails.html',{'form':form,})
    else: 
        return render(request,'tracking/pagenotfound.html')

@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)
def updateprofiledetailsadmin(request,pid):
    instance = get_object_or_404(ProfileDetails, user_id=pid)
    if request.method == "POST":
        form = ProfileDetailsForm(data = request.POST, files = request.FILES, instance = instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('journal:viewprofile',kwargs={'pid':pid}))
    else:
        form = ProfileDetailsForm(instance=instance)
    return render(request,'journal/createprofiledetails.html',{'form':form,})
            

def viewprofiledetails(request,pid):
    profile = get_object_or_404(ProfileDetails, user_id = pid)
    try:
        linkid = profile.journal.journallink.home
        extendname = 'journal/journalextend.html'
        return render(request,'journal/viewprofiledetails.html',{'profile':profile,'extendname':extendname, 'linkid':linkid})
    except:
        if request.user.id != int(pid):
            return render(request,'tracking/pagenotfound.html')
        extendname = 'tracking/htmlarcana.html'
        return render(request,'journal/viewprofiledetails.html',{'profile':profile,'extendname':extendname})

@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)
def createPublishedManuscriptAdmin(request):
    if request.method =='POST':
        form = PublishedManuscriptForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.save()
            return HttpResponseRedirect(reverse('fullarticle',kwargs={'aid':p.id}))
    else:
        form = PublishedManuscriptForm()
    return render(request,'journal/createpublishedmanuscript.html',{'form':form,})

 

@login_required(login_url='/tracking/login2')
@user_passes_test(lambda u: u.is_staff)
def updatePublishedManuscriptAdmin(request,pid):
    instance = get_object_or_404(PublishedManuscript, id=pid)
    form = PublishedManuscriptUpdateForm(request.POST or None, instance = instance)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('fullarticle',kwargs={'aid':pid}))
    return render(request,'journal/createpublishedmanuscript.html',{'form':form,})        

def journalhome(request):
    return render(request,'journal/home.html')

def submissioninstructions(request):
    return render(request,'journal/submissioninstructions.html')
def reviewerguidelines(request):
    return render(request,'journal/reviewerguidelines.html')
def contact(request):
    return render(request,'journal/contact.html')
def journallist(request):
    homelinks = JournalLink.objects.all()
    return render(request,'journal/journallist.html',{'homelinks':homelinks})


def journalpagehome(request,linkid):
    journallink = get_object_or_404(JournalLink,home=linkid)
    homeblock = get_object_or_404(JournalHome,journals = journallink.journals)
    return render(request,'journal/homepage.html',{'homeblock':homeblock,"linkid":linkid})

def journalarticle(request, linkid):
    journallink = get_object_or_404(JournalLink,home=linkid)
    published_list = PublishedManuscript.objects.filter(journal = journallink.journals).order_by('-create_time')
    paginator = Paginator(published_list,25)
    page = request.GET.get('page')
    try:
        publishedlists = paginator.page(page)
    except PageNotAnInteger:
        publishedlists = paginator.page(1)
    except EmptyPage:
        publishedlists = paginator.page(paginator.num_pages)
    return render (request,'journal/journalarticlepage.html',{'manuscripts':publishedlists,"linkid":linkid })
        
def articlefulldetails(request,aid,*args, **kwargs):
    article = get_object_or_404(PublishedManuscript,id=aid)
    linkid = article.journal.journallink.home
    return render (request,'journal/journalfullarticlepage.html',{'article':article,"linkid":linkid})

def journalebmembers(request,linkid):
    journallink = get_object_or_404(JournalLink,home=linkid)
    journal = Journals.objects.get(id=journallink.journals.id)
    #eblist = ProfileDetails.objects.filter(journal=journal).extra(select={'noarrange':'ISNULL(arrange)'},order_by=['noarrange','arrange'])
    eblist = ProfileDetails.objects.filter(journal=journal).order_by("-user__points__score").exclude(membertype="sub")
    paginator = Paginator(eblist,25)
    page = request.GET.get('page')
    try:
        eblists = paginator.page(page)
    except PageNotAnInteger:
        eblists = paginator.page(1)
    except EmptyPage:
        eblists = paginator.page(paginator.num_pages)
    return render (request,'journal/eblist.html',{'eblists':eblists,"linkid":linkid})

def journalinstructionsauthor(request,linkid):
    journallink = get_object_or_404(JournalLink,home=linkid)
    instructions = get_object_or_404(Instructions,journals=journallink.journals)
    return render(request,'journal/instructionspage.html',{'instructions':instructions,"linkid":linkid})



def journalabout(request,linkid):
    journallink = get_object_or_404(JournalLink,home=linkid)
    aboutjournal = get_object_or_404(AboutJournal,journals=journallink.journals)

    return render(request,'journal/about.html',{'aboutjournal':aboutjournal,"linkid":linkid})
     
def faqspage(request):
    return render(request,'journal/faqs.html')

def archive(request,year):
    published_list = PublishedManuscript.objects.filter(year = year).order_by('create_time')
    paginator = Paginator(published_list,25)
    page = request.GET.get('page')
    try:
        publishedlists = paginator.page(page)
    except PageNotAnInteger:
        publishedlists = paginator.page(1)
    except EmptyPage:
        publishedlists = paginator.page(paginator.num_pages)
    return render (request,'journal/yeararticlepage.html',{'manuscripts':publishedlists,'year':year })

def totalebmembers(request):
    eblist = ProfileDetails.objects.all().order_by("-user__points__score").exclude(membertype="sub")
    paginator = Paginator(eblist,25)
    page = request.GET.get('page')
    try:
        eblists = paginator.page(page)
    except PageNotAnInteger:
        eblists = paginator.page(1)
    except EmptyPage:
        eblists = paginator.page(paginator.num_pages)
    return render (request,'journal/eblisttotal.html',{'eblists':eblists})


def issue(request,volume,issue):
    published_list = PublishedManuscript.objects.filter(volume=volume, issue=issue).order_by('create_time')
    paginator = Paginator(published_list,25)
    page = request.GET.get('page')
    try:
        publishedlists = paginator.page(page)
    except PageNotAnInteger:
        publishedlists = paginator.page(1)
    except EmptyPage:
        publishedlists = paginator.page(paginator.num_pages)
    return render (request,'journal/issue.html',{'manuscripts':publishedlists,'volume':volume,'issue':issue })
    

def issuearchive(request):
    return render(request,'journal/archive.html')    
        
     
    
