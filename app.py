from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_limiter import Limiter
from flask import redirect
import validators
import requests
import io
import re
import base64
import bcrypt
import random
import string
import qrcode
from datetime import datetime
from io import BytesIO
from dotenv import load_dotenv
import os
from models import db, Nonprofit, RedirectLog

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
limiter = Limiter(key_func=lambda: request.remote_addr)


def is_valid_email(email):
    email_regex = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return email_regex.match(email)


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def generate_short_url(long_url):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return img_base64


def is_valid_url(url):
    return validators.url(url)


def is_valid_ein(ein):
    ein_regex = re.compile(r'^\d{2}-\d{7}$')
    return ein_regex.match(ein)


def verify_ein(ein):
    if not is_valid_ein(ein):
        return False
    api_key = os.getenv('CHARITY_API_KEY')
    url = f"https://api.charityapi.org/api/public_charity_check/{ein}"
    headers = {"apikey": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("data") and data["data"].get("public_charity"):
            return True
    return False


@app.route('/register', methods=['POST'])
@limiter.limit('5/minute')
def register():
    data = request.get_json()

    if 'name' not in data or 'email' not in data or 'password' not in data or 'long_url' not in data or 'ein' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    name = data['name'].strip()
    email = data['email'].strip()
    password = data['password'].strip()
    long_url = data.get('long_url', None)
    ein = data.get('ein', None).strip()

    if not name or not is_valid_email(
            email) or not password or not is_valid_url(
                long_url) or not is_valid_ein(ein):
        return jsonify({"error": "Invalid input"}), 400

    if Nonprofit.query.filter_by(ein=ein).first():
        return jsonify({"error": "EIN already registered"}), 409

    if not verify_ein(ein):
        return jsonify({"error": "Invalid EIN"}), 400

    if Nonprofit.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    hashed_password = hash_password(password)
    short_url = generate_short_url(long_url)
    base_url = request.url_root
    qr_code = generate_qr_code(f"{base_url}{short_url}")

    nonprofit = Nonprofit(name=name,
                          email=email,
                          password=hashed_password,
                          short_url=short_url,
                          long_url=long_url,
                          ein=ein,
                          qr_code=qr_code)
    db.session.add(nonprofit)
    db.session.commit()

    access_token = create_access_token(identity=nonprofit.id)
    return jsonify({
        "access_token": access_token,
        "nonprofit": {
            "id": nonprofit.id,
            "name": nonprofit.name,
            "email": nonprofit.email,
            "short_url": short_url,
            "qr_code": qr_code
        }
    }), 201


@app.route('/login', methods=['POST'])
@limiter.limit('5/minute')
def login():
    # Authenticate the nonprofit and return a JWT token
    pass


@app.route('/<short_url>', methods=['GET'])
def redirect_to_donation_page(short_url):
    nonprofit = Nonprofit.query.filter_by(short_url=short_url).first()
    if nonprofit:
        # Create a new RedirectLog entry and add it to the database
        log_entry = RedirectLog(nonprofit_id=nonprofit.id,
                                timestamp=datetime.utcnow())
        db.session.add(log_entry)
        db.session.commit()

        return redirect(nonprofit.long_url, code=303)
    else:
        return jsonify({"error": "Short URL not found"}), 404


if __name__ == '__main__':
    app.run()
