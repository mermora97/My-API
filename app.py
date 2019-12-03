from bottle import route, run, get, post, request
from mongo import DatabaseConnection
from recommender import recommendFriends
from slack import SlackApp
import json
import os

def slackToMongo(col,query):
    if len(col.find(query)) == 0:
        return None
    elif len(col.find(query)) == 1:
        return str(col.find(query)[0]['_id'])
    else:
        return [str(e['_id']) for e in col.find(query)]


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
    users = request.forms.getlist('user_id_list')
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
def getUsersListFromSlack(slack_token):
    slack = SlackApp(slack_token)
    name_filter = request.forms.get('name_filter','')
    
    users_list = slack.getTeamUsers(name_filter)
    for idx,user in enumerate(users_list):
        users_list[idx]['user_id'] = str(db.createUser(data=user))
    return {'results':users_list, 'total_results':len(users_list)}

@post('/slack/<slack_token>/post/message&channel=<channel>&text=<text>')
def getUsersList(slack_token,channel,text):
    slack = SlackApp(slack_token)
    res = slack.postMessage(text,channel)
    
    chat_id = slackToMongo(db.chats,{'slack_channel':channel})
    if chat_id:
        addMessage(chat_id, data={'user_id'=self.currentUser,'text'=text})
    else:
        chat_id = createChat(data={'user_id_list':[self.currentUser, res.get('message').get('user')})
        addMessage(chat_id, data={'user_id'=self.currentUser,'text'=text})

    return {'chat_id':chat_id}

db = DatabaseConnection('ChatDatabase')
run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))