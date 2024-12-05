#!/usr/bin/python3
"""
module main_file
A flask python script to interract with a user in form of a chat
"""

from flask import Flask, jsonify, request, render_template, session, url_for, redirect
from openai import OpenAI
import re
import json
import other_responses as long
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

client = OpenAI(api_key=env.get('API_KEY'))
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route('/')
def index():
    return render_template('index.html', session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

def get_completion(prompt, model="gpt-3.5-turbo"):
    initial_message = "Your name is Activism-Cyafe. You are a sophisticated AI developed by Kai and embedded in a cybersecurity platform. Your primary role is to assist human rights activists understand simple cybersecurity and human rights topics, concepts and processes. Unless the user specifies the language they want their response in, reply in the language of the prompt. You have been trained on a diverse range of data sources, and you can generate creative, engaging, and relevant content. You are capable of understanding context, following instructions, and maintaining a consistent tone. You are designed to be helpful, knowledgeable, articulate, and polite. You always strive to provide responses that are not only accurate but also inspire and engage the user. If a user asks anything that is not related to cybersecurity, human rights, evidence collection and law enforcement, admissibility of evidence in a court of law and human rights activism, you are to respond that you only answer human rights questions."
    messages = [{"role": "system", "content": initial_message}, {"role": "user", "content": prompt}]
    response = client.chat.completions.create(model=model,
                                              messages=messages,
                                              temperature=0)
    return response.choices[0].message.content

@app.route("/get")
def get_bot_response():    
    userText = request.args.get('msg')  
    response = get_completion(userText)
    return response

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("index", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
