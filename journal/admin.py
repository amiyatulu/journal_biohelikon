from django.contrib import admin
from journal.models import ProfileDetails, PublishedManuscript, \
    PublishedManuscriptRevisions, JournalLink, Instructions, AboutJournal, \
    JournalHome


class ProfileDetailsAdmin(admin.ModelAdmin):
    search_fields = ['address','research_interest','education','experience','publications','user__username','user__first_name','user__last_name','user__email']
    list_filter = ["membertype","journal__name","user__last_login"]

admin.site.register(ProfileDetails, ProfileDetailsAdmin)
admin.site.register(PublishedManuscript)
admin.site.register(PublishedManuscriptRevisions)
admin.site.register(JournalLink)
admin.site.register(Instructions)
admin.site.register(AboutJournal)
admin.site.register(JournalHome)