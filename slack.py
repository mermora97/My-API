from slacker import Slacker
import json
import requests

class SlackApp:

    def __init__(self,slack_token):
        print('Connecting to Slack application...')
        self.token = slack_token
        self.slack = Slacker(slack_token)
        testAuth = self.slack.auth.test().body
        self.team = testAuth['team']
        self.currentUser = testAuth['user']
        self.url = 'https://slack.com/api/chat'

    def getTeamUsers(self,name_filter = ''):
        users = self.slack.users.list().body['members']
        usersList = []
        for user in users:
            if name_filter in user['profile'].get('display_name',[]) or name_filter in user.get('real_name',[]):
                user_doc = {
                    'name':user.get('real_name',user.get('name')),
                    'slack_id':user.get('id'),
                    'email':user.get('profile').get('email'),
                    'phone':user.get('profile').get('phone'),
                    'status':user.get('profile').get('title')
                    }
                usersList.append(user_doc)
        return usersList
    
    def getPrivateChannels(slack):
        channels = []
        for idx,group in enumerate(slack.groups.list().body['groups']):
            channels[idx] = {'slack_channel':group['id'],'name':group['name'], 'members':group['members']}
            messages = []
            print("Getting history for private channel {0} with id {1}".format(group['name'], group['id']))
            messages = getHistory(slack.groups, group['id'])
            channels[idx]['messages'] = [m['text'] for m in messages]
        return channels

    def postMessage(self,channel,text):
        url = f'{self.url}.postMessage?token={self.token}&channel={channel}&text={text}&as_user=True&pretty=1'
        return requests.post(url).json()