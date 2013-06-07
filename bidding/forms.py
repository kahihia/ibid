from django import forms
from bidding import models
from bidding.models import ITEM_CATEGORY_CHOICES

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