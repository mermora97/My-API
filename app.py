from bottle import route, run, get, post, request
from mongo import DatabaseConnection
from recommender import recommendFriends
from slack import SlackApp
import json
import os

@route("/")
def index():
    return "Hello world!"

@post('/user/create')
def createUser():
    user = dict([i for i in request.forms.items()])
    return {
        'user_id':str(db.createUser(user))}

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

@route('/slack/<slack_token>/connect')
def slackConnect(slack_token):
    try:
        slack = SlackApp(slack_token)
        return 'Successfully authenticated for team {0} and user {1}.'.format(slack.team, slack.currentUser)
    except:
        return 'Error in slack identification'

@get('/slack/<slack_token>/users/list')
def getUsersList(slack_token):
    slack = SlackApp(slack_token)
    name_filter = request.forms.get('filter','')
    save = request.forms.get('save',False)
    
    usersList = slack.getTeamUsers(name_filter)
    if save:
        usersIdList = []
        for user in usersList:
            usersIdList.append(str(db.createUser(user)))
            return userIdList
    return usersList

db = DatabaseConnection('ChatDatabase')
run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))