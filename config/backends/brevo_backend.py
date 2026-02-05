import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class BrevoEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.configuration = sib_api_v3_sdk.Configuration()
        # سنستخدم EMAIL_HOST_PASSWORD كمفتاح API (API Key) لسهولة الإعداد في Render
        self.configuration.api_key['api-key'] = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(self.configuration))

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        
        count = 0
        for message in email_messages:
            try:
                sender = {"email": message.from_email or settings.DEFAULT_FROM_EMAIL}
                to = [{"email": recipient} for recipient in message.to]
                
                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=to,
                    sender=sender,
                    subject=message.subject,
                    html_content=message.body if message.content_subtype == 'html' else None,
                    text_content=message.body if message.content_subtype != 'html' else None,
                )
                
                # التعامل مع المرفقات إذا وجدت
                if hasattr(message, 'alternatives') and message.alternatives:
                    for content, mimetype in message.alternatives:
                        if mimetype == 'text/html':
                            send_smtp_email.html_content = content

                self.api_instance.send_transac_email(send_smtp_email)
                count += 1
            except ApiException as e:
                logger.error(f"Brevo API Error: {e}")
                if not self.fail_silently:
                    raise
            except Exception as e:
                logger.error(f"Error sending email via Brevo API: {e}")
                if not self.fail_silently:
                    raise
        return count
