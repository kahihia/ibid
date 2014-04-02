from django.contrib import admin
from django import forms

from chat.models import Message, AuctioneerPhrase
from chat.views import do_send_message


class MessageAdminForm(forms.ModelForm):
    def save(self, commit=True):
        instance = super(MessageAdminForm, self).save(commit=commit)
        
        if not instance.id:
            #just created
            do_send_message(instance)
        
        return instance
    
    class Meta:
        model = Message


class MessageAdmin(admin.ModelAdmin):
    form = MessageAdminForm
    list_display = ('content_type', 'user', 'created', 'text')
    fields = ('object_id','content_type', 'user', 'text', 'created')
    raw_id_fields = ('content_type',)
    readonly_fields = ('user',)
    

class ChatUserAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'object_id') 


class AuctioneerPhraseAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')


admin.site.register(AuctioneerPhrase, AuctioneerPhraseAdmin)
admin.site.register(Message, MessageAdmin)
