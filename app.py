from bottle import route, run, get, post, request
from mongo import DatabaseConnection
from recommender import recommendFriends
import json
import os

@get("/")
def index():
    return {
        "Hello":"world!"
    }

@post('/user/create')
def createUser():
    username = request.forms.get('username')
    return {
        'user_id':str(db.createUser(username))}

@get('/user/<user_id>/recommend')
def recommendFriend(user_id):
    userName = db.find({'_id':user_id},{ name: 1, _id: 0 })
    return recommendFriends(userName)

@post('/chat/create')
def createChat():
    users = request.forms.getlist('user_id')
    return {
        'chat_id':str(db.createChat(users))}

@post('/chat/<chat_id>/adduser')
def addUserToChat(chat_id):
    user = request.forms.get('user_id')
    return {
        'chat_id':str(db.addUserToChat(user,chat_id))}

@post('/chat/<chat_id>/addmessage')
def addMessage(chat_id):
    user = request.forms.get('user_id')
    text = request.forms.get('text')
    response = db.addMessage(user,chat_id,text)
    if type(response) == ValueError:
        return ValueError(str(response))
    else:            
        return {
            'chat_id':str(response)}
    
@get('/chat/<chat_id>/list')
def getMessages(chat_id):
    return json.dumps([{'message':m} for m in db.getMessages(chat_id)])

@get('/chat/<chat_id>/sentiment')
def analyzeMessages(chat_id):
    return {
        'sentiments': db.sentimentAnalysis(chat_id)}

db = DatabaseConnection('ChatDatabase')
run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))