import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# from dotenv import load_dotenv
import requests

def send_simple_message_py(to, subject, body):

    # load_dotenv()
    """Hàm gửi email xác nhận đăng ký"""
    sender_email = os.getenv("EMAIL_ACCOUNT")  # Thay bằng email của bạn
    sender_password = os.getenv("EMAIL_SECRET")  # Thay bằng mật khẩu ứng dụng (App Password) hoặc mật khẩu Gmail của bạn

    # Thiết lập nội dung email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to
    message["Subject"] = subject
    # Tạo nội dung email
    # body = "Chúc mừng bạn đã xác nhận đăng ký thành công!"
    message.attach(MIMEText(body, "plain"))
    try:
        # Thiết lập kết nối với server SMTP của Gmail
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Mã hóa kết nối
        server.login(sender_email, sender_password)  # Đăng nhập Gmail

        # Gửi email
        text = message.as_string()
        server.sendmail(sender_email, to, text)
        server.quit()
        print(f"Email xác nhận đã được gửi tới {to}.")
    except Exception as e:
        print(f"Không thể gửi email. Lỗi: {e}")


# def send_simple_message(to, subject, body):

#     domain = os.getenv("MAILGUN_DOMAIN")
#     print(domain, os.getenv("MAILGUN_API_KEY"))
#     return requests.post(
#             f"https://api.mailgun.net/v3/{domain}/messages",
#             auth=("api", os.getenv("MAILGUN_API_KEY")),
#             data={"from": f"Thiên Toàn <mailgun@{domain}>",
#                 "to": [to],
#                 "subject": subject,
#                 "text": body}
#             )

def send_simple_message(to, subject, body):
    domain = os.getenv("MAILGUN_DOMAIN")
    api_key = os.getenv("MAILGUN_API_KEY")

    if not domain or not api_key:
        print("Mailgun domain hoặc API Key không tồn tại.")
        return None

    response = requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data={
            "from": f"Thiên Toàn <mailgun@{domain}>",
            "to": [to],
            "subject": subject,
            "text": body
        }
    )
    
    if response.status_code == 200:
        print("Email đã được gửi thành công.")
    else:
        print(f"Không thể gửi email. Mã lỗi: {response.status_code}")
        print(f"Chi tiết lỗi: {response.text}")

    print(response)
    return response