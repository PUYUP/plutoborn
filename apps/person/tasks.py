import logging
import smtplib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.core.mail import BadHeaderError, EmailMultiAlternatives

# Celery config
from celery import shared_task

_PROJECT_NAME = settings.PROJECT_NAME
UserModel = get_user_model()


@shared_task
def send_otp_email(data):
    logging.info(_(u"Send OTP Code email run."))

    to = data.get('email', None)
    otp_code = data.get('otp_code', None)

    if to and otp_code:
        subject = _(u"Validasi OTP")
        from_email = '%s <hellopuyup@gmail.com>' % (_PROJECT_NAME)

        # Message
        text = _(
            "JANGAN BERIKAN KODE OTP ini kepada siapapun "
            "TERMASUK PIHAK %(site_name)s. Kode OTP Anda: " +
            otp_code
        ) % {'site_name': _PROJECT_NAME}

        html = _(
            "JANGAN BERIKAN KODE OTP ini kepada siapapun "
            "TERMASUK PIHAK %(site_name)s.<br />"
            "Kode OTP Anda: "
            "<strong>" + otp_code + "</strong>"
            "<br /><br />"
            "Salam, <br /> <strong>%(site_name)s</strong>"
        ) % {'site_name': _PROJECT_NAME}

        if subject and from_email:
            try:
                msg = EmailMultiAlternatives(subject, text, from_email, [to])
                msg.attach_alternative(html, "text/html")
                msg.send()
                logging.info(_(u"OTP Code email success."))
            except smtplib.SMTPConnectError as e:
                logging.error('SMTPConnectError: %s' % e)
            except smtplib.SMTPAuthenticationError as e:
                logging.error('SMTPAuthenticationError: %s' % e)
            except smtplib.SMTPSenderRefused as e:
                logging.error('SMTPSenderRefused: %s' % e)
            except smtplib.SMTPRecipientsRefused as e:
                logging.error('SMTPRecipientsRefused: %s' % e)
            except smtplib.SMTPDataError as e:
                logging.error('SMTPDataError: %s' % e)
            except smtplib.SMTPException as e:
                logging.error('SMTPException: %s' % e)
            except BadHeaderError:
                logging.warning(_(u"Invalid header found."))
    else:
        logging.warning(_(u"Tried to send email to non-existing OTP Code."))
