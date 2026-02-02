from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from .models import PostComment


class PostCommentForm(forms.ModelForm):
    """
    Form for adding comments to blog posts
    """
    class Meta:
        model = PostComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _('اكتب تعليقك هنا...')
            }),
        }
        labels = {
            'content': _('التعليق'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('content', css_class='form-control mb-3'),
            Submit('submit', _('إضافة تعليق'), css_class='btn btn-primary')
        )
