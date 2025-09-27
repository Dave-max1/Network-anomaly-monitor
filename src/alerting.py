import smtplib
import logging
# import requests
import json
from email.message import EmailMessage

class AlertManager:
    def __init__(self, cfg):
        self.cfg = cfg
        self.email_cfg = cfg.get('email', {})
        self.webhook_cfg = cfg.get('webhook', {})

    def alert(self, alert_type, context, message):
        # Always log
        logging.error("ALERT [%s] %s -- context=%s", alert_type, message, context)
        # email
        if self.email_cfg.get('enabled', False):
            self._send_email(alert_type, message)
        # webhook
        # if self.webhook_cfg.get('enabled', False):
        #     self._post_webhook(alert_type, context, message)

    def _send_email(self, alert_type, message):
        cfg = self.email_cfg
        try:
            msg = EmailMessage()
            msg['Subject'] = f"[NetWatcher] {alert_type}"
            msg['From'] = cfg['from_addr']
            msg['To'] = ", ".join(cfg['to_addrs'])
            msg.set_content(message)
            with smtplib.SMTP(cfg['smtp_host'], cfg.get('smtp_port', 25)) as s:
                s.starttls()
                s.login(cfg['username'], cfg['password'])
                s.send_message(msg)
            logging.info("Email sent for alert %s", alert_type)
        except Exception as e:
            logging.exception("Failed to send alert email: %s", e)

    # def _post_webhook(self, alert_type, context, message):
    #     try:
    #         payload = {'type': alert_type, 'message': message, 'context': context}
    #         r = requests.post(self.webhook_cfg['url'], json=payload, timeout=5)
    #         logging.info("Webhook posted status=%s", r.status_code)
    #     except Exception as e:
    #         logging.exception("Failed to post webhook: %s", e)
