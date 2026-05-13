from app.infrastructure.db.config import settings
from email.message import EmailMessage
import smtplib

class EmailService:

    def sendPointSaleLoginCode(self, toEmail: str, code: str) -> None:
        message = EmailMessage()
        message["Subject"] = "Código de acceso - Registro de domicilios"
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = toEmail

        message.set_content(
            f"""
                Hola,

                Tu código de acceso al aplicativo de Registro de domicilios es:

                {code}

                Este código vence en {settings.POINT_SALE_LOGIN_CODE_EXPIRE_MINUTES} minutos.

                Si no solicitaste este código, ignora este correo.
                """
        )

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()

            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

            smtp.send_message(message)