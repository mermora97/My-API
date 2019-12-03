from bottle import route, run, get, post, request
from mongo import DatabaseConnection
from recommender import recommendFriends
from slack import SlackApp
import json
import os

def slackToMongo(col,query):
    if len(list(col.find(query))) == 0:
        return None
    elif len(list(col.find(query))) == 1:
        return str(col.find(query)[0]['_id'])
    else:
        return [str(e['_id']) for e in list(col.find(query))]


@route("/")
def index():
    return "Welcome to my api!"

@get('/user_id')
def getUserId():
    user = dict([i for i in request.forms.items()])    
    return slackToMongo(col,query)

@post('/user/create')
def createUser():
    user = dict([i for i in request.forms.items()])
    return {
        'user_id':str(db.createUser(user))}

@get('/user/<user_id>/recommend')
def recommendFriend(user_id):
    return recommendFriends(user_id)

@post('/chat/create')
def createChat():
    users = request.forms.getlist('users_list')
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
    name_filter = request.forms.get('filter','')
    
    users_list = slack.getTeamUsers(name_filter)
    print('Searching for slack users...')
    print(f'{len(users_list)} users found in slack')
    for idx,user in enumerate(users_list):
        user_id = str(db.createUser(user))
        users_list[idx]['user_id'] = user_id
    return {'results':users_list, 'total_results':len(users_list)}

@get('/slack/<slack_token>/channels')
def getSlackChannels(slack_token):
    slack = SlackApp(slack_token)
    channels = slack.getPrivateChannels()
    print('Channels found---', channels)
    print(f'{len(channels)} channels found---')
    return {'results':channels,'total_results':len(channels)}

@post('/slack/<slack_token>/post/message&channel=<channel>&text=<text>')
def postSlackMessage(slack_token,channel,text):
    slack = SlackApp(slack_token)
    res = slack.postMessage(text,channel)

    print('Response...',res)
    if res.get('ok'):
        print('Message sent')
    else:
        return TypeError('Message error, could not be sent')
    
    chat_id = slackToMongo(db.chats,{'slack_channel':channel})
    if chat_id:
        db.addMessage(slack.currentUser,chat_id,text)
    else:
        print('Chat not found. Creating chat...')
        chat_id = str(db.createChat([slack.currentUser, res.get('message').get('user')]))
        db.addMessage(slack.currentUser,chat_id,text)
    return {'chat_id':chat_id}

db = DatabaseConnection('ChatDatabase')
run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))