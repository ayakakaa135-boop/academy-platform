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
        
        # الحصول على مفتاح API من الإعدادات
        api_key = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        
        # سجل تشخيصي (بدون طباعة المفتاح كاملاً للأمان)
        if not api_key:
            logger.error("Brevo API Key is missing! Check EMAIL_HOST_PASSWORD in environment variables.")
        else:
            logger.info(f"Brevo API Key found (starts with: {api_key[:5]}...)")
            
        self.configuration.api_key['api-key'] = api_key
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(self.configuration))

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        
        count = 0
        for message in email_messages:
            try:
                sender_email = message.from_email or settings.DEFAULT_FROM_EMAIL
                sender = {"email": sender_email, "name": "Academy Platform"}
                to = [{"email": recipient} for recipient in message.to]
                
                # استخراج محتوى HTML
                html_content = None
                if message.content_subtype == 'html':
                    html_content = message.body
                elif hasattr(message, 'alternatives'):
                    for content, mimetype in message.alternatives:
                        if mimetype == 'text/html':
                            html_content = content
                            break
                
                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=to,
                    sender=sender,
                    subject=message.subject,
                    html_content=html_content or message.body,
                    text_content=message.body if html_content else None,
                )
                
                logger.info(f"Attempting to send email to {message.to} via Brevo API...")
                api_response = self.api_instance.send_transac_email(send_smtp_email)
                logger.info(f"Email sent successfully! Message ID: {api_response.message_id}")
                count += 1
            except ApiException as e:
                logger.error(f"Brevo API Error (Status {e.status}): {e.body}")
                if not self.fail_silently:
                    raise
            except Exception as e:
                logger.error(f"Unexpected error sending email: {str(e)}")
                if not self.fail_silently:
                    raise
        return count
