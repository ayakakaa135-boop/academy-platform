from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from allauth.account.utils import send_email_confirmation
from django.contrib import messages

class CustomAccountAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        """
        تخصيص التحقق من البريد الإلكتروني للتمييز بين المستخدمين المفعّلين وغير المفعّلين.
        """
        # استدعاء التحقق الافتراضي أولاً (يتحقق من الصيغة وما إلى ذلك)
        email = super().clean_email(email)
        
        # التحقق مما إذا كان البريد موجوداً مسبقاً
        email_address = EmailAddress.objects.filter(email__iexact=email).first()
        
        if email_address:
            if email_address.verified:
                # إذا كان الحساب مفعلاً، نترك السلوك الافتراضي (سيتم رفع خطأ "موجود مسبقاً")
                return email
            else:
                # إذا كان الحساب موجوداً ولكن غير مفعل
                # نقوم بإرسال رابط تفعيل جديد
                request = self.request
                user = email_address.user
                if user:
                    send_email_confirmation(request, user, signup=False)
                
                # نرفع خطأ مخصص يخبر المستخدم بأنه تم إرسال رابط تفعيل جديد
                raise ValidationError(
                    _("هذا البريد الإلكتروني مسجل مسبقاً ولكن لم يتم تفعيله. لقد أرسلنا لك رابط تفعيل جديد، يرجى التحقق من بريدك الإلكتروني.")
                )
        
        return email
