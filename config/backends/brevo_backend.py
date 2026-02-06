import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class BrevoEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        
        # الحصول على مفتاح API من الإعدادات
        # تحويل إلى string لحل مشكلة lazy proxy من decouple
        api_key = str(getattr(settings, 'EMAIL_HOST_PASSWORD', '')).strip()
        
        if not api_key or api_key == 'None':
            logger.error("Brevo API Key is missing! Check EMAIL_HOST_PASSWORD in environment variables.")
            self.api_instance = None
            return
        
        try:
            logger.info(f"Brevo API Key found (starts with: {api_key[:5]}...)")
            
            self.configuration = sib_api_v3_sdk.Configuration()
            self.configuration.api_key['api-key'] = api_key
            
            self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
                sib_api_v3_sdk.ApiClient(self.configuration)
            )
            logger.info("Brevo API client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Brevo API client: {str(e)}")
            self.api_instance = None
            if not fail_silently:
                raise

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        
        if self.api_instance is None:
            logger.error("Brevo API client is not initialized. Cannot send emails.")
            if not self.fail_silently:
                raise RuntimeError("Brevo API client not initialized")
            return 0
        
        count = 0
        for message in email_messages:
            try:
                sender_email = message.from_email or settings.DEFAULT_FROM_EMAIL
                sender = {"email": sender_email, "name": "Academy Platform"}
                to = [{"email": recipient} for recipient in message.to]
                
                # استخراج محتوى HTML
                # في Django، عند استخدام EmailMultiAlternatives، يتم تخزين HTML في alternatives
                html_content = None
                
                # 1. التحقق من وجود محتوى HTML في alternatives (الطريقة الشائعة)
                if hasattr(message, 'alternatives'):
                    logger.info(f"Message has {len(message.alternatives)} alternatives")
                    for content, mimetype in message.alternatives:
                        logger.info(f"Alternative mimetype: {mimetype}")
                        if mimetype == 'text/html':
                            html_content = content
                            logger.info("HTML content found in alternatives")
                            break
                
                # 2. إذا لم يوجد، التحقق مما إذا كان الرسالة نفسها من نوع HTML
                if not html_content:
                    subtype = getattr(message, 'content_subtype', None)
                    logger.info(f"Message content_subtype: {subtype}")
                    if subtype == 'html' or '<html>' in message.body.lower():
                        html_content = message.body
                        logger.info("HTML content found in message body")
                
                # إعداد كائن الإرسال
                # نستخدم html_content إذا وجد، وإلا نستخدم message.body كـ HTML بسيط
                final_html = html_content
                if not final_html:
                    # التحقق من وجود وسوم HTML في الجسم حتى لو لم يتم تحديد النوع
                    if '<html>' in message.body.lower() or '<body' in message.body.lower() or '<div' in message.body.lower():
                        final_html = message.body
                        logger.info("HTML tags detected in body, using as final_html")
                    else:
                        final_html = f"<html><body dir='rtl'>{message.body.replace(chr(10), '<br>')}</body></html>"

                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=to,
                    sender=sender,
                    subject=message.subject,
                    html_content=final_html,
                    text_content=message.body,
                )

                logger.info(f"Attempting to send email to {message.to} via Brevo API (HTML: {'Yes' if html_content else 'No'})...")
                if html_content:
                    logger.info(f"HTML Content length: {len(html_content)}")
                    logger.info(f"HTML Snippet: {html_content[:500]}...")
                
                api_response = self.api_instance.send_transac_email(send_smtp_email)
                logger.info(f"Email sent successfully! Message ID: {api_response.message_id}")
                count += 1
                
            except ApiException as e:
                logger.error(f"Brevo API Error (Status {e.status}): {e.body}")
                if not self.fail_silently:
                    raise
            except AttributeError as e:
                # Handle swagger_types or other attribute errors
                logger.error(f"Attribute error in Brevo API: {str(e)}. This may indicate a configuration issue.")
                if not self.fail_silently:
                    raise
            except Exception as e:
                logger.error(f"Unexpected error sending email: {str(e)}")
                if not self.fail_silently:
                    raise
        
        return count
