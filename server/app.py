#!/usr/bin/env python3

# Standard library imports

# Remote library imports
from flask import request,jsonify,session
from flask_restful import Resource
import requests
import base64
from datetime import datetime




# Local imports
from config import app, db, api,bcrypt
# Add your model imports
from models import User,Payment

#Daraja configurarion
CONSUMER_KEY = 'Acanbo61MoPTMXW9xfaNAtEv580CyM70YyGEfqGHziNMsqNC'
CONSUMER_SECRET = '9AEtSPvIMzDEpJn4IEg4MISqtsTXm32SEBWdQjDBWKeb0RZCcM3wGuWsn98jD3fA'

# Views go here!


class UserRegistration(Resource):
    def register(self):
        data= request.get_json()
        username = data.get('username')
        email= data.get('email')
        password=data.get('password')
        if not username or not email or not password:
            return jsonify({'message': 'Some required fields are missind'}),400
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'message':'User already exists'}),400
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commimt()
        return jsonify({'message':'User created successfully'}),201

class UserLogin(Resource):
    def login(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'message':'Email or Password missing'}),400
        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.check_password_hash(user.password,password):
            return jsonify({'error':'Invalid email or password'}),401
        
        session['user_id'] = user.id
        return jsonify({'message':'Login successful'}),200
    
# @app.route("/get_token")
def get_access_token():
    consumer_key = CONSUMER_KEY
    consumer_secret = CONSUMER_SECRET
    access_token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    headers = {"Content-Type":"application/json"}
    auth = (consumer_key,consumer_secret)
    try:
        response = requests.get(access_token_url,headers=headers,auth=auth)
        response.raise_for_status()
        result = response.json()
        access_token = result["access_token"]
        return jsonify({"access_token":access_token})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)})
    
@app.route('/pay')
def MpesaExpress():
    data = request.get_json()
    phone_number = data.get("phone_number")
    amount = data.get("amount")

    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    access_token = get_access_token()
    headers = {"Authorization": "Bearer %s" % access_token}
    times = datetime.now().strftime("%Y%m%H%M%S")
    password = "174379" + "Cbfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919" + times
    password = base64.b64decode(password.encode('utf-8'))

    payload = {
    "BusinessShortCode": 174379,
    "Password": password,
    "Timestamp": times,
    "TransactionType": "CustomerPayBillOnline",
    "Amount": amount,
    "PartyA": phone_number,
    "PartyB": 174379,
    "PhoneNumber": phone_number,
    "CallBackURL": "https://mydomain.com/path",
    "AccountReference": "CompanyXLTD",
    "TransactionDesc": "Payment of X" 
  }

    response = requests.request("POST", 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', headers = headers, data = payload)
    return response.json()



    

api.add_resource(UserLogin, '/login')
api.add_resource(UserRegistration,'/register')



if __name__ == '__main__':
    app.run(port=5555, debug=True)

