from django.contrib import admin
from mailing.models import EmailList, JTemplate, JournalEmailDetails


class EmailListAdmin(admin.ModelAdmin):
    list_display = ('email','name','affiliation',)
    search_fields = ['email','name','affiliation']
    list_filter = ['subscription']

admin.site.register(EmailList, EmailListAdmin)
admin.site.register(JTemplate)
admin.site.register(JournalEmailDetails)