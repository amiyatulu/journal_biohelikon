from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from tracking.models import Manuscript, Journals, UploadFile, Reviewer, Review, \
    ReviewComment, UploadReview, ManuscriptComment, ManuscriptAccessCode, \
    ManuscriptStatus, ReviewerBuffer, UploadedManuscriptVisibility, Points


class MyUserAdmin(UserAdmin):
    list_filter = UserAdmin.list_filter + ('last_login',)



class ManuscriptAdmin(admin.ModelAdmin):
    list_filter = ('journal','create_time','update_time',)

    

class UploadFileAdmin(admin.ModelAdmin):
    list_filter = ('manuscript',) 

class ReviewerBufferAdmin(admin.ModelAdmin):
    list_filter = ('manuscript',)

class ManuscriptStatusAdmin(admin.ModelAdmin):
    list_filter = ('status',)  


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)    
admin.site.register(Manuscript, ManuscriptAdmin)
admin.site.register(Journals)
admin.site.register(UploadFile, UploadFileAdmin)
admin.site.register(Reviewer)
admin.site.register(Review)
admin.site.register(ReviewComment)
admin.site.register(UploadReview)
admin.site.register(ManuscriptStatus, ManuscriptStatusAdmin)
admin.site.register(ManuscriptComment)
admin.site.register(ManuscriptAccessCode)
admin.site.register(ReviewerBuffer,ReviewerBufferAdmin)
admin.site.register(UploadedManuscriptVisibility)
admin.site.register(Points)

