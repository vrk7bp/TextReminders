#This is the file to define your constants which are used throughout the backend web server

SCOPES = 'https://www.googleapis.com/auth/calendar email openid profile' #Scopes of information you want from Google
APPLICATION_NAME = #Name of your Google application

DB_PATH = #Local path to your DB

GOOGLE_LOGIN_CLIENT_ID = #Your client ID
GOOGLE_LOGIN_CLIENT_SECRET = #Your Google Secret

OAUTH_CREDENTIALS={
        'google': {
            'id': GOOGLE_LOGIN_CLIENT_ID,
            'secret': GOOGLE_LOGIN_CLIENT_SECRET
        }
}

ACCOUNT_SID = #Your Twilio Account SID
AUTH_TOKEN = #Your Twilio Auth Token

TWILIO_NUMBER = #Your Twilio phone number
MOM_NUMBER = #Main business number
GAUTAM_NUMBER = #Developer number, so they get updates too
