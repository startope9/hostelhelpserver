import os
import json
from firebase_admin import credentials, db, firestore
import firebase_admin
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)

CORS(app, supports_credentials=True, resources={
     r"/api/*": {"origins": 'https://hostelhelphub.vercel.app/'}}, methods=['GET', 'POST'])

firebase_credentials = os.environ.get('FIREBASE_CREDENTIALS_JSON')
cred = credentials.Certificate(json.loads(firebase_credentials))
firebase_admin.initialize_app(cred)

db = firestore.client()


@app.route('/home', methods=['GET'])
def greet():
    return "Hello from flask"


@app.route('/adminlog', methods=['POST'])
def admincredential():

    req = request.get_json()

    users_ref = db.collection(u'Admin')
    docs = users_ref.stream()

    for doc in docs:
        print(doc.to_dict())
        if req['Head'] == doc.to_dict()['Head'] and req['Password'] == doc.to_dict()['Password']:
            return '200'

    return '500'


@app.route('/upload_prob', methods=['POST'])
def problems():

    req = request.get_json()

    doc_ref = db.collection(u'Problems').document()

    try:
        doc_ref.set(req)
        return '200'
    except:
        return '500'


@app.route('/get_data/<string:check_solve>', methods=['POST'])
def send_probs(check_solve):

    users_ref = db.collection(u'Problems')
    docs = users_ref.stream()

    arr = []
    if check_solve == 'unsolved':
        for doc in docs:
            if not doc.to_dict()['solved']:
                arr.append([doc.id,  doc.to_dict()['roomNo'],  doc.to_dict()[
                           'Prob'], doc.to_dict()['vote_count'], doc.to_dict()['solved']])

    elif check_solve == 'solved':
        for doc in docs:
            if doc.to_dict()['solved']:
                arr.append([doc.id,  doc.to_dict()['roomNo'],  doc.to_dict()[
                           'Prob'], doc.to_dict()['vote_count'], doc.to_dict()['solved']])

    return arr


@app.route('/likeaction/<string:what>', methods=['POST'])
def addAction(what):

    users_ref = db.collection(u'Problems')

    req = request.get_json()["ID"]

    docs = users_ref.stream()

    for doc in docs:
        if doc.id == req and what == 'dislike':
            db.collection(u'Problems').document(doc.id).update(
                {"vote_count": doc.to_dict()['vote_count']-1})
            print(f'{doc.id} => {doc.to_dict()}')
            break

        if doc.id == req and what == 'like':
            db.collection(u'Problems').document(doc.id).update(
                {"vote_count": firestore.Increment(1)})
            print(f'{doc.id} => {doc.to_dict()}')
            break

    return '200'


@app.route('/handlesolved', methods=['POST'])
def solved():
    req = request.get_json()['ID']
    users_ref = db.collection(u'Problems')
    docs = users_ref.stream()

    for doc in docs:
        if doc.id == req:
            db.collection(u'Problems').document(doc.id).update({"solved": 1})
            break

    return '200'


if __name__ == '__main__':
    app.run(debug=False)
