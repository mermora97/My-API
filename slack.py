from slacker import Slacker

class SlackApp:

    def __init__(self,slack_token):
        print('Connecting to Slack application...')
        self.slack = Slacker(slack_token)
        testAuth = self.slack.auth.test().body
        self.team = testAuth['team']
        self.currentUser = testAuth['user']

    def getTeamUsers(self,name_filter = ''):
        users = self.slack.users.list().body['members']
        userIdNameMap = {}
        for user in users:
            if name_filter in user['profile'].get('display_name',[]) or name_filter in user.get('real_name',[]):
                userIdNameMap[user['id']] = user
        return userIdNameMap
    