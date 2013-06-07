from django.contrib import admin
from chat.models import Message, AuctioneerPhrase
from django import forms
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
    list_display = ('auction', 'user', 'created', 'text')
    fields = ('auction', 'user', 'text', 'created')
    raw_id_fields = ('auction',)
    readonly_fields = ('user',)

    
admin.site.register(Message, MessageAdmin)

class ChatUserAdmin(admin.ModelAdmin):
    list_display = ('user', ) 

class AuctioneerPhraseAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')
    #readonly_fields = ('key', 'description')

admin.site.register(AuctioneerPhrase, AuctioneerPhraseAdmin)