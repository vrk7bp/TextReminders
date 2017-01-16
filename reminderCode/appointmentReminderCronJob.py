import sqlite3
import constants
import requests
import datetime
import re
import sendReminder
import sys
from rfc3339 import rfc3339

listOfUsers = ['viennakumon@gmail.com', 'vrk7bp@virginia.edu']

#Pulls OAUTH refresh tokens from SQLite DB
def getRefreshTokensForUsers(listOfApprovedUsers):
	listOfIDs = []
	conn = sqlite3.connect('oauthTokens.db')
	c = conn.cursor()
	d = conn.cursor()
	for email in listOfApprovedUsers:
		tempTuple = (email, )
		idList = c.execute('SELECT id FROM userInfo WHERE email=?', tempTuple)
		for row in idList:
			otherTempTuple = (row[0], )
			tokenList = d.execute('SELECT refresh_token FROM refreshTokens WHERE id=?', otherTempTuple)
			for otherRow in tokenList:
				newTuple = (email, otherRow[0])
				listOfIDs.append(newTuple)

	return listOfIDs

#Uses refresh token to grab access token for current query
def get_access_token(refresh_token):
	credentials = constants.OAUTH_CREDENTIALS[provider_name]
	request_data = {'refresh_token': refresh_token, 'client_id': credentials['id'], 'client_secret': credentials['secret'], 'grant_type': 'refresh_token'}
	return requests.post('https://www.googleapis.com/oauth2/v4/token', data=request_data).json().get('access_token')

#Grabs access tokens for each user that is trying to send reminder texts
def getNewAccessTokens(listOfRefreshTokens):
	listOfAccessTokens = []
	for tokens in listOfRefreshTokens:
		x = get_access_token(tokens[1])
		newTuple = (tokens[0], x)
		listOfAccessTokens.append(newTuple)

	return listOfAccessTokens

#Grabs list of events for each user
def getListOfCalendarEventsForDay(accessTokenList):
	listOfJsonCalendarLists = []
	for access_token_tuple in accessTokenList:
		access_token = access_token_tuple[1]
		info = getCalendarInformationForUser(access_token)
		calendar_tuple = (access_token_tuple[0], info)
		listOfJsonCalendarLists.append(calendar_tuple)
	
	listOfUserTuplesWithFormattedEvents = []
	for tuples in listOfJsonCalendarLists:
		listOfEventsForUser = []
		for eventEntry in tuples[1]['items']:
			eventTuple = (eventEntry.get('id'), eventEntry.get('summary'), eventEntry.get('description'), eventEntry.get('start').get('dateTime'))
			listOfEventsForUser.append(eventTuple)
		listOfUserTuplesWithFormattedEvents.append((tuples[0], listOfEventsForUser))
	return listOfUserTuplesWithFormattedEvents

# Parses calendar events and then uses Twilio to send text based reminders.
def sendOutRemindersBasedOnEvents(listOfFormattedEvents):
	listOfRemindersSent = []
	listOfRemindersNotSent = []
	for user in listOfFormattedEvents:
		userName = user[0]
		listOfEvents = user[1]
		for event in listOfEvents:
			id = event[0]
			summary = event[1]
			description = event[2]
			startDateTime = event[3]
			if summary is None:
				listOfRemindersNotSent.append(("No summary provided", event))
				continue
			number = re.search('(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', summary)
			if(number is None or number.group(0) == None):
				listOfRemindersNotSent.append(("No number deteced", event))
			else:
				if(summary.lower().find("no text") is -1):
					onlyNumber = re.sub("[^0-9]", "", number.group(0))
					if(len(onlyNumber) is not 10):
						listOfRemindersNotSent.append(("Invalid number deteced", event))
					successful =  sendReminder.sendText(onlyNumber, startDateTime)
					if(successful):
						listOfRemindersSent.append(event)
					else:
						listOfRemindersNotSent.append(("Bad number/text failed", event))
				else:
					listOfRemindersNotSent.append(("No text requested", event))

	sendReminder.synopsisText(listOfRemindersSent, listOfRemindersNotSent)
	return (listOfRemindersSent, listOfRemindersNotSent)

# Helper method for getListOfCalendarEventsForDay
def getCalendarInformationForUser(accessToken, calendarName='primary'):
        headers = {'Authorization': 'Bearer {}'.format(accessToken)}
	startTime = getRFCTimeForTomorrowMorning()
	endTime = getRFCTimeForTomorrowNight()
	parameters = {'timeMin': startTime, 'timeMax': endTime}
	return requests.get('https://www.googleapis.com/calendar/v3/calendars/{}/events'.format(calendarName), params=parameters, headers=headers).json()

# This method is hard-coded for East Coast time. Has to be changed for other timezones.
def getRFCTimeForTomorrowMorning():
	tomorrowsDate = datetime.datetime.today() + datetime.timedelta(days=1)
	formattedDate = tomorrowsDate.replace(hour=5, minute=0, second=0, microsecond=0)
	return rfc3339(formattedDate, utc=True)

# This method is hard-coded for East Coast time. Has to be changed for other timezones.
def getRFCTimeForTomorrowNight():
	tomorrowsDate = datetime.datetime.today() + datetime.timedelta(days=2)
	formattedDate = tomorrowsDate.replace(hour=5, minute=0, second=0, microsecond=0)
	return rfc3339(formattedDate, utc=True)

def mainMethod(startingList):
	try:
		print
		print "Starting appointment reminders for {}".format(str(datetime.datetime.today()))
		idList = getRefreshTokensForUsers(startingList)
		print "ID List: " + str(idList)
		accessTokenList = getNewAccessTokens(idList)
		print "Access Token List: " + str(accessTokenList)
		calendarList = getListOfCalendarEventsForDay(accessTokenList)
		print "Calendar List: " + str(calendarList)
		
		# Part of script that deals with sending reminders
		returnTuple = sendOutRemindersBasedOnEvents(calendarList)
		print "List of reminders sent: " + str(returnTuple[0])
		print "List of reminders not sent: " + str(returnTuple[1])
		print "End appointment reminders for {}".format(str(datetime.datetime.today()))
		print
	except:
		sendReminder.failureTextToGautam("In main method")
		sys.exc_info()[0]
		raise		

mainMethod(listOfUsers)
