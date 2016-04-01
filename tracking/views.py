from __future__ import division

import datetime
from decimal import Decimal
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt
import operator
from smtplib import SMTPRecipientsRefused, SMTPSenderRefused

from journal.models import ProfileDetails
from tracking.models import RegistrationForm, ManuscriptForm, JournalsForm, \
    UploadFile, Manuscript, Review, ReviewComment, ReviewForm, Reviewer, \
    UploadReview, ManuscriptComment, ManuscriptAccessCode, AccessCodeForm, \
    ManuscriptStatus, UserProfileForm, ChangePassword, ManuscriptAdminForm, \
    ReviewerBuffer, UploadedManuscriptVisibility, UserVoted, ReviewPoints, \
    Points, UserVotedManuscript, ManuscriptPoints, InboxCount, Notification, \
    upvoteordownvoteNotify


def register(request):
    if request.user.is_anonymous():
        if request.method == 'POST' and 'myregister' in request.POST:
            form = RegistrationForm(request.POST)
            
            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                address = form.cleaned_data['address']
                research_interest = form.cleaned_data['research_interest_keywords']
                user = User.objects.create_user(username,email,password)
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                ProfileDetails.objects.create(user=user, address = address, research_interest= research_interest)
                state = "Registration Successful, Please login..."
                return render(request,'registration/registrationsuccessful.html',{'state': state,})
        else:
            form = RegistrationForm()    
        return render(request,'registration/register.html',{'form':form,
                                                })
    else:
        return HttpResponseRedirect(reverse("tracking:home"))

def home(request):
    return render(request,'tracking/htmlarcana.html')

def newlogin(request):
    if request.user.is_anonymous():
        state = "Please log in below..."
        username = password = ''
        if 'mylogin' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    state = "You're successfully logged in!"
                    return HttpResponseRedirect(reverse('tracking:home'))
                else:
                    state = "Your account is not active, please contact the site admin."
            else:
                state = "Your username and/or password were incorrect."
        return render(request,'registration/loginunsuccessfull.html',{'state': state})
    else:
        return HttpResponseRedirect(reverse('tracking:home'))
def login2(request):
    if request.user.is_anonymous():
        state = "Please log in below..."
        username = password = ''
        nexty = request.GET.get('next')
        
        if 'mylogin' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    state = "You're successfully logged in!"
                    if nexty is not None:
                        return HttpResponseRedirect(nexty)
                    return HttpResponseRedirect(reverse('tracking:home'))
                else:
                    state = "Your account is not active, please contact the site admin."
            else:
                state = "Your username and/or password were incorrect."
        return render(request,'registration/loginunsuccessfull.html',{'state': state,'next':nexty})
    else:
        return HttpResponseRedirect(reverse('tracking:home'))
    
@login_required(login_url='/tracking/login2')    
def manuscriptSubmission(request):
    if request.method == 'POST':
        form = ManuscriptForm(request.POST)
        if form.is_valid():
            manuscript = form.save(commit=False)
            manuscript.user = request.user
            manuscript.save()
            access = ManuscriptAccessCode(manuscript=manuscript)
            access.save()
            manuscriptstatus = ManuscriptStatus(manuscript=manuscript,status="RV")
            manuscriptstatus.save()
            
            
            return HttpResponseRedirect(reverse('tracking:uploadfile',kwargs={'mid':manuscript.id}))
    else:
        form = ManuscriptForm()
    return render(request,'tracking/manuscript.html',{'form':form,
                                                       })
    
def createJournal(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = JournalsForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('')
        else:
            form = JournalsForm()
        return render (request, 'tracking/createjournal.html',{'form':form,
                                                           })
    else:
        return render(request,'tracking/pagenotfound.html')



@csrf_exempt
@login_required(login_url='/tracking/login2') 
def dropZone(request,mid):
    try:
        manus= Manuscript.objects.get(pk=mid)
        if manus.user_id != request.user.id:
            return render(request,'tracking/pagenotfound.html')
    except:
        return render(request,'tracking/pagenotfound.html')
    if request.method == 'POST':
        if UploadFile.objects.filter(manuscript=manus):
            manu = UploadFile.objects.filter(manuscript=manus).order_by('-id')[0]
            rev = manu.revision + 1
        else:
            rev = 1
        for i in request.FILES.getlist('url'):
            m = UploadFile(files=i,manuscript=manus,user=request.user,revision=rev,create_time= datetime.datetime.utcnow().replace(tzinfo=utc))
            try:
                m.full_clean()
                m.save()
                
            except ValidationError:
                pass
        return HttpResponseRedirect(reverse('tracking:manuscriptdetails',kwargs={'mid':mid}))    
    return render(request, 'tracking/uploadform.html',{'manus':manus}) 

@login_required(login_url='/tracking/login2')
def manuscriptlisting(request):
    manuscript_list = Manuscript.objects.filter(user=request.user).order_by('-create_time')
    if manuscript_list :
        paginator = Paginator(manuscript_list,25)
        page = request.GET.get('page')
        try:
            manuscripts = paginator.page(page)
        except PageNotAnInteger:
            manuscripts = paginator.page(1)
        except EmptyPage:
            manuscripts = paginator.page(paginator.num_pages)
        
        return render(request, 'tracking/manuscriptlist.html',{"manuscripts": manuscripts})
    else:
        return render(request,'tracking/nomanuscriptlist.html')

@login_required(login_url='/tracking/login2')
def manuscriptview(request,mid):
    try:
        manu = Manuscript.objects.get(pk=mid)
        if manu.user_id != request.user.id:
            return render(request,'tracking/pagenotfound.html')
    except:
        return render(request,'tracking/pagenotfound.html')
    uploads = UploadFile.objects.filter(manuscript=manu).order_by('revision')
    return render(request,'tracking/manuscriptdetail.html',{"manuscript":manu,"uploads":uploads})  

@login_required(login_url='/tracking/login2')
def manuscriptupdate(request,mid):
    try:
        instance = Manuscript.objects.get(pk=mid)
        if instance.user_id != request.user.id:
            return render(request,'tracking/pagenotfound.html')
    except:
        return render(request,'tracking/pagenotfound.html')
    form = ManuscriptForm(request.POST or None, instance=instance)
    if form.is_valid():
            manuscript = form.save(commit=False)
            manuscript.save()
            return HttpResponseRedirect(reverse('tracking:manuscriptdetails',kwargs={'mid':manuscript.id}))
    return render(request,'tracking/manuscript.html',{'form':form,
                                                       }) 
    
@login_required(login_url='/tracking/login2')
def commentpage(request,mid):
    manuscript = get_object_or_404(Manuscript, id=mid)
    reviewerpresent = Reviewer.objects.filter(manuscript_id = mid, user_id = request.user.id)
    if reviewerpresent or manuscript.user_id == request.user.id or request.user.is_superuser :
        uploads =  UploadFile.objects.filter(manuscript=manuscript).order_by('revision')
        review = Review.objects.filter(manuscript=manuscript)
        reviewpresent = Review.objects.filter(manuscript=manuscript,user= request.user)
        reviewupload = UploadReview.objects.filter(manuscript=manuscript)
        manuscriptcomment = ManuscriptComment.objects.filter(manuscript=manuscript)
        reviewers = Reviewer.objects.filter(manuscript_id = mid)
        return render(request, 'tracking/commentpage.html',{'manuscript':manuscript,"uploads":uploads, "review":review,"reviewpresent":reviewpresent, "reviewupload":reviewupload, "manuscriptcomment":manuscriptcomment, "reviewers":reviewers})
    else:
        return render(request,'tracking/pagenotfound.html')

@login_required(login_url='/tracking/login2')
def ajaxcreatereview(request,mid):
    reviewerpresent = Reviewer.objects.filter(manuscript_id = mid, user_id = request.user.id)
    reviewpresent = Review.objects.filter(manuscript_id=mid,user= request.user)
    manuscript = get_object_or_404(Manuscript,id=mid)
    if not reviewerpresent:
        return render(request,'tracking/pagenotfound.html')
    if reviewpresent:
        return render(request,'tracking/pagenotfound.html')
    if manuscript.user_id == request.user.id:
        return render(request,'tracking/pagenotfound.html')
    if request.POST and request.is_ajax():
        title = request.POST['title']
        originality = request.POST['originality']
        typo_errors = request.POST['typo_errors']
        deepness = request.POST['deepness']
        comprehensible = request.POST['comprehensible']
        overall_comments = request.POST['overall_comments']
        if  not title  and  not originality  and not typo_errors  and not deepness  and not comprehensible  and not overall_comments:
            return render(request,'tracking/pagenotfound.html')
        else:        
            review = Review(manuscript_id= mid, user=request.user, title = title, originality = originality, typo_errors=typo_errors, deepness=deepness, comprehensible= comprehensible,overall_comments=overall_comments)
            review.save()
        return render(request,'tracking/createreview.html',{'review':review, 'mid':mid})

@login_required(login_url='/tracking/login2')
def updatereview(request,rid):
    instance = get_object_or_404(Review, id=rid)
    if instance.user_id != request.user.id:
        return render(request,'tracking/pagenotfound.html')
    form = ReviewForm(request.POST or None, instance=instance)
    if form.is_valid():
        review = form.save(commit=False)
        review.save()
        return HttpResponseRedirect(reverse('tracking:commentpage',kwargs={'mid':instance.manuscript_id}))
    return render(request,'tracking/updatereview.html',{'form':form,
                                                        })
@login_required(login_url='/tracking/login2')
def ajaxaddcomment(request,rid,mid):
    reviewerpresent = Reviewer.objects.filter(manuscript_id = mid, user_id = request.user.id)
    manuscript = get_object_or_404(Manuscript,id=mid)
    review = get_object_or_404(Review, id= rid)
    if reviewerpresent or manuscript.user_id == request.user.id:
            if request.POST and request.is_ajax():
                comment = request.POST['comment']
                if not comment:
                    return render(request,'tracking/pagenotfound.html')
                else:
                    reviewcomment = ReviewComment(review = review, user_id = request.user.id, comment = comment)
                    reviewcomment.save()
                return render(request,'tracking/addreviewcomment.html',{'reviewcomment':reviewcomment,})
    else:
        return render(request,'tracking/pagenotfound.html')

@csrf_exempt
@login_required(login_url='/tracking/login2') 
def dropReviewZone(request,mid):
    reviewerpresent = Reviewer.objects.filter(manuscript_id = mid, user_id = request.user.id)
    manuscript = get_object_or_404(Manuscript,id=mid)
    review = Review.objects.filter(user_id= request.user.id, manuscript_id=mid)
    if not review:
        return render(request,'tracking/pagenotfound.html')
    if not reviewerpresent:
        return render(request,'tracking/pagenotfound.html')
    if manuscript.user_id == request.user.id:
        return render(request,'tracking/pagenotfound.html')
    if request.method == 'POST':
        for i in request.FILES.getlist('url'):
            print(i.name)
            m = UploadReview(reviewfile=i,manuscript=manuscript,user=request.user,create_time= datetime.datetime.utcnow().replace(tzinfo=utc))
            try:
                m.full_clean()
                m.save()
            except ValidationError:
                pass
        return HttpResponseRedirect(reverse('tracking:manuscriptdetails',kwargs={'mid':mid}))
                
    return render(request, 'tracking/uploadreviewform.html',{'manuscript':manuscript})



@login_required(login_url='/tracking/login2') 
def ajaxaddmanuscriptcomment(request,mid):
    reviewerpresent = Reviewer.objects.filter(manuscript_id = mid, user_id = request.user.id)
    manuscript = get_object_or_404(Manuscript,id=mid)
    if reviewerpresent or manuscript.user_id == request.user.id:
        if request.POST and request.is_ajax():
                comment = request.POST['comment']
                if not comment:
                    return render(request,'tracking/pagenotfound.html')  
                else:
                    manuscriptcomment = ManuscriptComment(manuscript = manuscript, user_id = request.user.id, comment = comment)
                    manuscriptcomment.save()
                return render(request,'tracking/addmanuscriptcomment.html',{'manuscriptcomment':manuscriptcomment,})
    else:
        return render(request,'tracking/pagenotfound.html')

@login_required(login_url='/tracking/login2') 
def enteraccesscode(request):
    if request.POST:
        form = AccessCodeForm(request.POST)
        if form.is_valid():
            accesscode = form.cleaned_data['accesscode']
            try:
                maccesscode = ManuscriptAccessCode.objects.get(accesscode = accesscode)
                if maccesscode.manuscript.user == request.user:
                    error = "You cannot review your own manuscript."
                    return render(request,'tracking/accesscode.html',{'form':form,'error':error
                                                       })
                
                rev = Reviewer.objects.filter(manuscript= maccesscode.manuscript, user = request.user)
                if rev:
                    error = "You are already reviewer of this manuscript"
                    return render(request,'tracking/accesscode.html',{'form':form,'error':error
                                                       })
                else:
                    reviewer = Reviewer(manuscript = maccesscode.manuscript,user = request.user)
                    reviewer.save()
                    return HttpResponseRedirect(reverse('tracking:commentpage',kwargs={'mid':maccesscode.manuscript.id}))
                    
            except:
                error="Access Code does not exist."
                return render(request,'tracking/accesscode.html',{'form':form,'error':error
                                                       })
    else:
        form = AccessCodeForm()
    return render(request,'tracking/accesscode.html',{'form':form,
                                                       })
@login_required(login_url='/tracking/login2') 
def reviewtab(request):
    review_list = Reviewer.objects.filter(user=request.user).order_by('-create_time')
    paginator = Paginator(review_list, 25)
    if review_list:
        page = request.GET.get('page')
        try:
            reviews = paginator.page(page)
        except PageNotAnInteger:
            reviews = paginator.page(1)
        except EmptyPage:
            reviews = paginator.page(paginator.num_pages)
    
        return render(request,'tracking/reviewtab.html',{
                                                      "reviews":reviews
                                                     })
    else:
        return render(request,'tracking/nomanuscriptreview.html')


@login_required(login_url='/tracking/login2')
def updateprofile(request,pid):
    instance = get_object_or_404(User, id=pid)
    if instance.id != request.user.id:
        return render(request,'tracking/pagenotfound.html')
    form = UserProfileForm(request.POST or None, instance=instance)
    if form.is_valid():
        profile = form.save(commit=False)
        profile.save()
        return HttpResponseRedirect(reverse('tracking:home'))
    return render(request,'tracking/updateprofile.html',{'form':form,
                                                        })

@login_required(login_url='/tracking/login2')
def resetpassword(request):
    if request.method == 'POST':
        form = ChangePassword(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            u = User.objects.get(id = request.user.id)
            u.set_password(password)
            u.save()
            return HttpResponseRedirect(reverse('tracking:home'))
    else:
        form = ChangePassword()
    return render(request,'tracking/updatepassword.html',{'form':form,})
            
    
@login_required(login_url='/tracking/login2')
def admincreatemanuscript(request):
    if not request.user.is_superuser:
        return render(request,'tracking/pagenotfound.html')
    if request.method == 'POST':
        form = ManuscriptAdminForm(request.POST)
        if form.is_valid():
            manuscript = form.save(commit=False)
            manuscript.save()
            access = ManuscriptAccessCode(manuscript=manuscript)
            access.save()
            manuscriptstatus = ManuscriptStatus(manuscript=manuscript,status="RV")
            manuscriptstatus.save()
            
            
            return HttpResponseRedirect(reverse('tracking:adminuploadfile',kwargs={'mid':manuscript.id}))
    else:
        form = ManuscriptAdminForm()
    return render(request,'tracking/manuscript.html',{'form':form,
                                                       })

@csrf_exempt
@login_required(login_url='/tracking/login2') 
def admindropZone(request,mid):
    if not request.user.is_superuser:
        return render(request,'tracking/pagenotfound.html')
    try:
        manus= Manuscript.objects.get(pk=mid)
    except:
        return render(request,'tracking/pagenotfound.html')
    if request.method == 'POST':
        if UploadFile.objects.filter(manuscript=manus):
            manu = UploadFile.objects.filter(manuscript=manus).order_by('-id')[0]
            rev = manu.revision + 1
        else:
            rev = 1
        for i in request.FILES.getlist('url'):
            m = UploadFile(files=i,manuscript=manus,user=manus.user,revision=rev,create_time= datetime.datetime.utcnow().replace(tzinfo=utc))
            try:
                m.full_clean()
                m.save()
            except ValidationError as e:
                print(e)
                
    return render(request, 'tracking/adminuploadform.html',{'manus':manus})

@login_required(login_url='/tracking/login2') 
def adminmanuscriptlist(request):
    if not request.user.is_superuser:
        return render(request,'tracking/pagenotfound.html')
    manuscript_list = Manuscript.objects.all().order_by('-create_time')
    if manuscript_list :
        paginator = Paginator(manuscript_list,25)
        page = request.GET.get('page')
        try:
            manuscripts = paginator.page(page)
        except PageNotAnInteger:
            manuscripts = paginator.page(1)
        except EmptyPage:
            manuscripts = paginator.page(paginator.num_pages)
        
        return render(request, 'tracking/adminmanuscriptlist.html',{"manuscripts": manuscripts})
    else:
        return render(request,'tracking/nomanuscriptlist.html') 

@login_required(login_url='/tracking/login2') 
def adminmanuscriptdetails(request,mid):
    if not request.user.is_superuser:
        return render(request,'tracking/pagenotfound.html') 
    try:
        manu = Manuscript.objects.get(pk=mid)
    except:
        return render(request,'tracking/pagenotfound.html')
    uploads = UploadFile.objects.filter(manuscript=manu).order_by('revision')
    return render(request,'tracking/adminmanuscriptdetail.html',{"manuscript":manu,"uploads":uploads})

@login_required(login_url='/tracking/login2') 
def adminmanuscriptupdate(request,mid):
    if not request.user.is_superuser:
        return render(request,'tracking/pagenotfound.html')
    try:
        instance = Manuscript.objects.get(pk=mid)
    except:
        return render(request,'tracking/pagenotfound.html')
    form = ManuscriptAdminForm(request.POST or None, instance=instance)
    if form.is_valid():
            manuscript = form.save(commit=False)
            manuscript.save()
            return HttpResponseRedirect(reverse('tracking:adminmanuscriptdetails',kwargs={'mid':manuscript.id}))
    return render(request,'tracking/manuscript.html',{'form':form,
                                                       })   


@login_required(login_url='/tracking/login2')
def reviewerbuffer(request,mid):
    if request.user.is_superuser:
        ReviewerBufferFormSet = modelformset_factory(ReviewerBuffer,exclude=('manuscript','create_time'))    
        if request.method == 'POST':
            formset = ReviewerBufferFormSet(request.POST)
            if formset.is_valid():
                instances = formset.save(commit=False)
                query_rejected = []
                err= []
                for instance in instances:
                    instance.manuscript_id = mid
                    mail = instance.email
                    try:
                        instance.save()
                        
                    
                    except SMTPRecipientsRefused:
                        query_rejected.append(mail)
                        error="SMTP Recipients Refused"
                        err.append(error)
                    except UnicodeEncodeError:
                        query_rejected.append(mail)
                        error="Unicode Error"
                        err.append(error)
                    except SMTPSenderRefused:
                        query_rejected.append(mail)
                        error="SMTP Sender Refused"
                        err.append(error)
                    except:
                        query_rejected.append(mail)
                        error="Unique Constraint Error"
                        err.append(error)
                        
                    
                return render(request,'tracking/reviewerbuffererror.html',{'mail':query_rejected,'err':err,})
        else:
            formset = ReviewerBufferFormSet(queryset= ReviewerBuffer.objects.none())
        return render (request, 'tracking/createreviewerbuffer.html',{'formset':formset,
                                                           })
    else:
        return render(request,'tracking/pagenotfound.html')
    

@login_required(login_url='/tracking/login2')
def manuscriptvisible(request):
    visibility = UploadedManuscriptVisibility.objects.filter(user = request.user)
    jr = []
    for  vis in visibility:        
        jr.append(vis.journal)
    if visibility :    
        query = reduce(operator.or_,(Q(journal=x) for x in jr))
        manuscript_list = Manuscript.objects.filter(query).exclude(Q(manuscriptstatus__status = 'AC')|Q(manuscriptstatus__status = 'PB')).order_by('-create_time')
    
        paginator = Paginator(manuscript_list,25)
        page = request.GET.get('page')
        try:
            manuscripts = paginator.page(page)
        except PageNotAnInteger:
            manuscripts = paginator.page(1)
        except EmptyPage:
            manuscripts = paginator.page(paginator.num_pages)
        
        return render(request, 'tracking/manuscriptaccesslist.html',{"manuscripts": manuscripts})
    else:
        return render(request,'tracking/nomanuscriptaccesslist.html')

@login_required(login_url='/tracking/login2')
def reviewersdetails(request, mid):
    if request.user.is_superuser:
        reviewers = Reviewer.objects.filter(manuscript = mid)
        return render(request, 'tracking/reviewerdetails.html',{"reviewers":reviewers})


    
@login_required(login_url='/tracking/login2')    
def voting(request,rid):
    if request.method == 'POST':
        vote = request.POST.get('vote',None)
        review = Review.objects.get(pk = rid)
        try:
            points = Points.objects.get(user = review.user)
        except ObjectDoesNotExist:
            points = Points(user= review.user)
            points.score = 10
            points.ewallet = Decimal(10/4).quantize(Decimal('.00'))
        cantvote = ""
        uservoted  = UserVoted.objects.filter(review_id = rid,user = request.user)
        if uservoted:
            cantvote = "X"
            return HttpResponse(cantvote)
        elif review.user_id == request.user.id:
            cantvote = "Z"
            return HttpResponse(cantvote) 
        else:
            uservotedinstance = UserVoted(review_id=rid, user=request.user)
            uservotedinstance.save()
            try:
                reviewpoints = ReviewPoints.objects.get(pk = rid)
                if vote == "1":
                    reviewpoints.score = reviewpoints.score + 1
                    points.score = points.score + 10
                    points.ewallet = points.ewallet + Decimal(10/4).quantize(Decimal('.00'))
                    points.save()
                    upvoteordownvoteNotify(1,review.user)
                if vote == "0":
                    reviewpoints.score = reviewpoints.score - 1
                    points.score = points.score - 6
                    points.ewallet = points.ewallet - Decimal(6/4).quantize(Decimal('.00'))
                    points.save()
                    upvoteordownvoteNotify(0,review.user)
                reviewpoints.save()
            except ObjectDoesNotExist:
                if vote == "1":
                    reviewpointsinstance = ReviewPoints.objects.create(review_id=rid, score = 1)
                    reviewpointsinstance.save()
                    points.score = points.score + 10
                    points.ewallet = points.ewallet + Decimal(10/4).quantize(Decimal('.00'))
                    points.save()
                    upvoteordownvoteNotify(1,review.user)
                if vote == "0":
                    reviewpointsinstance = ReviewPoints.objects.create(review_id=rid, score = -1)
                    reviewpointsinstance.save()
                    points.score = points.score - 6
                    points.ewallet = points.ewallet - Decimal(6/4).quantize(Decimal('.00'))
                    points.save()
                    upvoteordownvoteNotify(0,review.user)
            
            votes = ReviewPoints.objects.get(pk = rid)
            return HttpResponse(votes.score)
        
@login_required(login_url='/tracking/login2')
def manuscriptVoting(request,mid):
    if request.method == 'POST':
        vote = request.POST.get('vote',None)
        manuscript = Manuscript.objects.get(pk = mid)
        try:
            points = Points.objects.get(user = manuscript.user)
        except ObjectDoesNotExist:
            points = Points(user= manuscript.user)
            points.score = 10
            points.ewallet = 10/4
        cantvote = ""
        uservoted = UserVotedManuscript.objects.filter(manuscript_id = mid, user = request.user)
        if uservoted:
            cantvote = "X"
            return HttpResponse(cantvote)
        elif manuscript.user_id == request.user.id:
            cantvote = "Z"
            return HttpResponse(cantvote)
        else:
            uservotedinstance = UserVotedManuscript(manuscript_id = mid, user = request.user)
            uservotedinstance.save()
            try:
                manuscriptpoints = ManuscriptPoints.objects.get(pk= mid)
                if vote == "1":
                    manuscriptpoints.score = manuscriptpoints.score + 1
                    points.score = points.score + 10
                    points.ewallet = points.ewallet + Decimal(10/4).quantize(Decimal('.00'))
                    points.save()
                    upvoteordownvoteNotify(1,manuscript.user)
                if vote == "0":
                    manuscriptpoints.score = manuscriptpoints.score - 1
                    points.score = points.score - 6
                    points.ewallet = points.ewallet - Decimal(6/4).quantize(Decimal('.00'))
                    points.save()
                    upvoteordownvoteNotify(0,manuscript.user)
                manuscriptpoints.save()
            except ObjectDoesNotExist:
                if vote == "1":
                    manuscriptpointsinstance = ManuscriptPoints.objects.create(manuscript_id=mid, score = 1)
                    manuscriptpointsinstance.save()
                    points.score = points.score + 10
                    points.ewallet = points.ewallet + Decimal(10/4).quantize(Decimal('.00'))
                    points.save()
                    upvoteordownvoteNotify(1,manuscript.user)
                if vote == "0":
                    manuscriptpointsinstance = ManuscriptPoints.objects.create(manuscript_id=mid, score = -1)
                    manuscriptpointsinstance.save()
                    points.score = points.score - 6
                    points.ewallet = points.ewallet - Decimal(6/4).quantize(Decimal('.00'))
                    points.save()
                    upvoteordownvoteNotify(0,manuscript.user)
            
            votes = ManuscriptPoints.objects.get(pk = mid)
            return HttpResponse(votes.score)


@login_required(login_url='/tracking/login2')
def resetInboxCount(request):
    if request.method == "POST":
        try:
            inbox = InboxCount.objects.get(user = request.user)
            inbox.count = 0
        except ObjectDoesNotExist:
            inbox = InboxCount(user = request.user, count = 0)
            
        inbox.save()
        return HttpResponse(inbox.count)


@login_required(login_url='/tracking/login2')
def fetchNotification(request):
    if request.method == "POST":
        query = Notification.objects.filter(user = request.user).order_by('-create_time')[:10]
        return render(request, 'tracking/notification.html',{"notif": query})
    


def activitiesDetails(request,uid):
    profile = get_object_or_404(ProfileDetails, user_id = uid)
    if profile.membertype == "eb" or profile.membertype == "rv":
        review = Review.objects.filter(user_id = uid).order_by('-create_time')
        usy = User.objects.get(pk = uid)
        
        return render(request, 'tracking/activitiesdetails.html',{"review":review, "usy":usy})
    if request.user.is_authenticated() and request.user.id == int(uid):
        review = Review.objects.filter(user_id = uid).order_by('-create_time')
        usy = User.objects.get(pk = uid)
        
        return render(request, 'tracking/activitiesdetails.html',{"review":review, "usy":usy})
        
    else:
        return render(request,'tracking/pagenotfound.html')    
