from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import CustomUser


class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information
    """
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'bio', 'avatar', 'date_of_birth']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'first_name': _('الاسم الأول'),
            'last_name': _('اسم العائلة'),
            'email': _('البريد الإلكتروني'),
            'phone': _('رقم الهاتف'),
            'bio': _('نبذة عني'),
            'avatar': _('الصورة الشخصية'),
            'date_of_birth': _('تاريخ الميلاد'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('phone', css_class='form-group col-md-6 mb-3'),
            ),
            Field('date_of_birth', css_class='form-control mb-3'),
            Field('bio', css_class='form-control mb-3'),
            Field('avatar', css_class='form-control mb-3'),
            Submit('submit', _('حفظ التغييرات'), css_class='btn btn-primary')
        )
