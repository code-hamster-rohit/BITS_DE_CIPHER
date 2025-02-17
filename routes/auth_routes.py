from fastapi import APIRouter
from models.auth_models import GenerateOtp, Login, Token
from email.mime.multipart import MIMEMultipart
from passlib.context import CryptContext
from config.connection import client
from email.mime.text import MIMEText
import random, smtplib, os
from bson import ObjectId

router = APIRouter()

def gen_otp(length: int):
    otp = ''
    for _ in range(length):
        otp += str(random.randint(0, 9))
    return otp

def send_otp(email: str, otp: str):
    msg = MIMEMultipart()
    msg['From'] = os.getenv('EMAIL_FROM')
    msg['To'] = email
    msg['Subject'] = '[Bits De Cipher] OTP Verification'
    body = f'''
Hey there!

A request to login to your account has been made.
Please use the following OTP to verify your email address: -

OTP: {otp}

If you did not make this request, you can safely ignore this email.

Thanks,
Bits De Cipher Team
'''
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
        server.connect(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT')))
        server.starttls()
        server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
        server.sendmail(os.getenv('EMAIL_FROM'), email, msg.as_string())
        server.quit()

def tokenize(password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

@router.post('/generate_otp')
async def generate_otp(creds: GenerateOtp):
    with client.start_session() as session:
        try:
            session.start_transaction()
            creds.email = creds.email.lower()
            user = client['2025']['OTP'].find_one({'email': creds.email}, session=session)
            otp = gen_otp(6)
            if user:
                client['2025']['OTP'].update_one({'email': creds.email}, {'$set': {'otp': otp}}, session=session)
            else:
                client['2025']['OTP'].insert_one({'_id': ObjectId(), 'email': creds.email, 'otp': otp}, session=session)
            send_otp(creds.email, otp)
            session.commit_transaction()
            return {'message': 'OTP sent successfully'}
        except Exception as e:
            session.abort_transaction()
            return {'message': str(e)}


@router.post('/login')
async def login(creds: Login):
    with client.start_session() as session:
        try:
            session.start_transaction()
            creds.email = creds.email.lower()
            otp = client['2025']['OTP'].find_one({'email': creds.email}, session=session)
            if otp['otp'] == creds.otp:
                token = tokenize(creds.email + creds.email[::-1])
                client['2025']['USER_INFO'].insert_one({'_id': ObjectId(), 'email': creds.email, 'password': token}, session=session)
                client['2025']['USER_QUESTION_NUMBER'].insert_one({'_id': ObjectId(), 'email': creds.email, 'latest_question_number': 1}, session=session)
                client['2025'].create_collection(creds.email, session=session)
                session.commit_transaction()
                return {'message': 'Login successful', 'token': token}
            else:
                session.commit_transaction()
                return {'message': 'Invalid OTP', 'token': ''}
        except Exception as e:
            session.abort_transaction()
            return {'message': str(e)}
    client.close()

@router.post('/check')
async def check(token: Token):
    with client.start_session() as session:
        try:
            session.start_transaction()
            user = client['2025']['USER_INFO'].find_one({'password': token.token}, session=session)
            if user:
                session.commit_transaction()
                return {'message': 'Valid token', 'user': user['email']}
            else:
                session.commit_transaction()
                return {'message': 'Invalid token', 'user': ''}
        except Exception as e:
            session.abort_transaction()
            return {'message': str(e)}
    client.close()