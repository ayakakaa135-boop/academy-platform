from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from .models import Comment, Review


class CommentForm(forms.ModelForm):
    """
    Form for adding comments to lessons
    """
    class Meta:
        model = Comment
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


class ReviewForm(forms.ModelForm):
    """
    Form for adding course reviews
    """
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} ★') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': _('شارك تجربتك مع هذه الدورة...')
            }),
        }
        labels = {
            'rating': _('التقييم'),
            'comment': _('التعليق'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('rating', css_class='mb-3'),
            Field('comment', css_class='form-control mb-3'),
            Submit('submit', _('إرسال التقييم'), css_class='btn btn-primary')
        )
