import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()
url_mongo_atlas = os.getenv('URL_ATLAS')

class DatabaseConnection:

    def __init__(self,dbName):
        print('Initializing database...')
        self.client = MongoClient(url_mongo_atlas)
        self.db = self.client[dbName]
        self.users = self.db['users']
        self.chats = self.db['chats']

    def createUser(self,name):
        doc = self.users.insert_one({'name':name})
        return doc.inserted_id
    
    def createChat(self,users):
        doc = self.chats.insert_one({'users':users})
        return doc.inserted_id
    
    def addUserToChat(self,user,chat):
        chat_doc = self.chats.find({'_id':ObjectId(chat)})[0]
        chat_doc['users'].append(user)
        self.chats.update_one({'_id':ObjectId(chat)},{'$set':{'users':chat_doc['users']}})
        return chat_doc['_id']

    def checkUserInChat(self,user,chat):
        chat_doc = self.chats.find({'_id':ObjectId(chat)})[0]
        if user not in chat_doc['users']:
            raise ValueError('Not allowed to writte in this conversation')

    def addMessage(self,user,chat,text):
        try:
            self.checkUserInChat(user,chat)
            self.chats.update_one({'_id':ObjectId(chat),'messages':{'$exists':False}},
                {'$set':{'messages':[]}})

            chat_doc = self.chats.find({'_id':ObjectId(chat)})[0]
            chat_doc['messages'].append(text)
            self.chats.update_one({'_id':ObjectId(chat)},{'$set':{'messages':chat_doc['messages']}})
            return chat_doc['_id']
        except ValueError as e:
            return ValueError(e)
        
    def getMessages(self,chat):
        chat_doc = self.chats.find({'_id':ObjectId(chat)})[0]
        return chat_doc['messages']

    def sentimentAnalysis(self,chat):
        chat_doc = self.chats.find({'_id':ObjectId(chat)})
        #Analyze chat_doc['messages']
        return ['sad','angry','happy']