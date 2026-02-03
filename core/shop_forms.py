from django import forms


class CheckoutForm(forms.Form):
    # Contact
    name = forms.CharField(max_length=140)
    company = forms.CharField(max_length=180, required=False)
    phone = forms.CharField(max_length=60, required=False)
    email = forms.EmailField()

    # Address
    address_label = forms.CharField(max_length=80, required=False, initial="Delivery")
    address_1 = forms.CharField(max_length=200, label="Address line 1")
    address_2 = forms.CharField(max_length=200, required=False, label="Address line 2")
    city = forms.CharField(max_length=120, required=False)
    county = forms.CharField(max_length=120, required=False)
    postcode = forms.CharField(max_length=30, required=False)
    country = forms.CharField(max_length=80, required=False, initial="United Kingdom")

    # Order
    order_number = forms.CharField(max_length=80, required=False, label="PO / Order Number")
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
