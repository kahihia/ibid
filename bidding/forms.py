from django import forms
from exceptions import ValueError

from bidding import models
from bidding.models import ITEM_CATEGORY_CHOICES, CONFIG_KEY_TYPES


class ConfigKeyAdminForm(forms.ModelForm):
    class Meta:
        model = models.ConfigKey

    value_type = forms.ChoiceField(choices=list(CONFIG_KEY_TYPES),
                                   label='Data type',
                                   required=True)

    def clean(self):
        super(ConfigKeyAdminForm, self).clean()
        
        key = self.cleaned_data.get('key')
        value = self.cleaned_data.get('value')
        value_type = self.cleaned_data.get('value_type')
        
        if (value_type == 'boolean' and value not in ('yes','no')):
            msg = u"Data_type is set to boolean. Value must be 'yes' or 'no'."
            self._errors['value'] = self.error_class([msg])
            del self.cleaned_data['value']
        elif (value_type == 'int'):
            try:
                long(value)
            except ValueError:
                msg = u"Data type is set to int. Value must be a number."
                self._errors['value'] = self.error_class([msg])
                del self.cleaned_data['value']
        return self.cleaned_data
    

class ItemAdminForm(forms.ModelForm):
    category = forms.ChoiceField(choices=[('', 'All')] + list(ITEM_CATEGORY_CHOICES), 
                                 label='Category', required=False)
    
    def clean(self):
        super(ItemAdminForm, self).clean()
        
        retail = self.cleaned_data.get('retail_price')
        total =  self.cleaned_data.get('total_price')
        
        if retail and total and retail > total:
            msg = u"The total price can't be lower than the retail price."
            self._errors['total_price'] = self.error_class([msg])
            del self.cleaned_data['total_price']
            
        return self.cleaned_data
    
    class Meta:
        model = models.Item
    

class AuctionAdminForm(forms.ModelForm):

    def _validate_minimum(self):
        precap = self.cleaned_data.get('precap_bids')
        minimum = self.cleaned_data.get('minimum_precap')
        
        if precap and minimum and minimum > precap / 2:
            msg = u"The minimum precap should be at most half of the total precap bids."
            self._errors['minimum_precap'] = self.error_class([msg])
            del self.cleaned_data['minimum_precap']
            
    
    #FIXME uns solo metodo generico y ya
    def _validate_threshold_bidding(self, field_low, field_high):
        low = self.cleaned_data.get(field_low)
        high = self.cleaned_data.get(field_high)
        
        if low and high and low >= high:
            msg = u"Each threshold should be lower than its predecesor."
            self._errors[field_low] = self.error_class([msg])
            del self.cleaned_data[field_low]
    
    def clean(self):
        super(AuctionAdminForm, self).clean()
        
        self._validate_minimum()
        
        self._validate_threshold_bidding('threshold1', 'bidding_time')
        
        self._validate_threshold_bidding('threshold2', 'bidding_time')
        self._validate_threshold_bidding('threshold2', 'threshold1')
        
        self._validate_threshold_bidding('threshold3', 'bidding_time')
        self._validate_threshold_bidding('threshold3', 'threshold1')
        self._validate_threshold_bidding('threshold3', 'threshold2')
                    
        return self.cleaned_data
    
    class Meta:
        model = models.Auction


"""
Forms and validation code for user registration.

Note that all of these forms assume Django's bundle default ``User``
model; since it's not possible for a form to anticipate in advance the
needs of custom user models, you will need to write your own forms if
you're using a custom model.

"""


from models import Member
from django import forms
from django.utils.translation import ugettext_lazy as _


class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.
    
    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.
    
    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.

    """
    required_css_class = 'required'
    
    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                label=_("Username"),
                                error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    email = forms.EmailField(label=_("E-mail"))
    password1 = forms.CharField(widget=forms.PasswordInput,
                                label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label=_("Password (again)"))
    
    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        existing = Member.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(_("A user with that username already exists."))
        else:
            return self.cleaned_data['username']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data


class RegistrationFormTermsOfService(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which adds a required checkbox
    for agreeing to a site's Terms of Service.
    
    """
    tos = forms.BooleanField(widget=forms.CheckboxInput,
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")})


class RegistrationFormUniqueEmail(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which enforces uniqueness of
    email addresses.
    
    """
    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        
        """
        if Member.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']


class RegistrationFormNoFreeEmail(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which disallows registration with
    email addresses from popular free webmail services; moderately
    useful for preventing automated spam registrations.
    
    To change the list of banned domains, subclass this form and
    override the attribute ``bad_domains``.
    
    """
    bad_domains = ['aim.com', 'aol.com', 'email.com', 'gmail.com',
                   'googlemail.com', 'hotmail.com', 'hushmail.com',
                   'msn.com', 'mail.ru', 'mailinator.com', 'live.com',
                   'yahoo.com']
    
    def clean_email(self):
        """
        Check the supplied email address against a list of known free
        webmail domains.
        
        """
        email_domain = self.cleaned_data['email'].split('@')[1]
        if email_domain in self.bad_domains:
            raise forms.ValidationError(_("Registration using free email addresses is prohibited. Please supply a different email address."))
        return self.cleaned_data['email']
