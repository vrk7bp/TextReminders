import datetime
import iso8601
import sys
import constants
from twilio.rest import TwilioRestClient

# Code to send the appointment remdiner text to the person who scheduled the appointment
def sendText(number, startDateTime):
	account_sid = constants.ACCOUNT_SID
	auth_token = constants.AUTH_TOKEN
	client = TwilioRestClient(account_sid, auth_token)
	timeTuple = convertRFC3339ToTimeString(startDateTime)
	timeString = timeTuple[0] + ":" + timeTuple[1] + " " + timeTuple[2]
	
	try:
		message = client.messages.create(to="+1{}".format(number), from_=constants.TWILIO_NUMBER,
        	                             body="Reminder: You have a {} appointment at Kumon of Vienna tomorrow. Please text or call {} if you have to make any changes. Note: This is an automated message, any reply to this number will not be read.".format(timeString, constants.MOM_NUMBER))
		print "Message for {} appointment was sent correctly".format(timeString)
	except:
		failureTextToGautam("{} appointment message not sent".format(timeString))
		print sys.exc_info()[0]
		return False;

	return True;

# Code to the send the synopsis text to make sure the events went through
def synopsisText(listOfSuccesses, listOfFailures):
	if(len(listOfSuccesses) + len(listOfFailures) is 0):
		print "No summary text sent because no events found"
		return True

	account_sid = constants.ACCOUNT_SID
	auth_token = constants.AUTH_TOKEN
	client = TwilioRestClient(account_sid, auth_token)
	
	successfulMessages = "We were able to send reminders for the following events: "
	unsuccessfulMessages = "We weren't able to send reminders for the following events: "
	
	for successes in listOfSuccesses:
		summaryText = successes[1]
		if successes[1] is None:
			timeTuple = convertRFC3339ToTimeString(successes[3])
			summaryText = timeTuple[0] + ":" + timeTuple[1] + " " + timeTuple[2] + " appointment"

		successfulMessages = successfulMessages + "\n" + summaryText

	for failures in listOfFailures:
                summaryText = failures[1][1]
                if failures[1][1] is None:
                        timeTuple = convertRFC3339ToTimeString(failures[1][3])
                        summaryText = timeTuple[0] + ":" + timeTuple[1] + " " + timeTuple[2] + " appointment"

		unsuccessfulMessages = unsuccessfulMessages + "\n" + "\"" + summaryText + "\"" + " because of " + failures[0]

	finalMessage = "Here is what I was able to send today: " + "\n" + successfulMessages + "\n" + unsuccessfulMessages
	try:
		message = client.messages.create(to=constants.MOM_NUMBER, from_=constants.TWILIO_NUMBER,
        	                             body=finalMessage)
		message = client.messages.create(to=constants.GAUTAM_NUMBER, from_=constants.TWILIO_NUMBER,
                	                     body=finalMessage)
		print "Synopsis messages were sent correctly"
	except:
		failureTextToGautam("Synopsis messages not sent correctly")
		print sys.exc_info()[0]
		return False;

	return True;

# Hard coded to not take into account Time Zone offset... assumes East Coast time
def convertRFC3339ToTimeString(startDateTime):
	dateTimeObject = iso8601.parse_date(startDateTime)
	hours = dateTimeObject.hour
	minutes = dateTimeObject.minute
	partOfDay = "AM"

	if(hours > 12):
		hours = hours - 12
		partOfDay = "PM"
	elif(hours == 0):
		hours = 12

	if(minutes < 10):
		minutes = "0" + str(minutes)

	return (str(hours), str(minutes), partOfDay)

# Failure case, sends me a text if there was any error that came up
def failureTextToGautam(details):
	account_sid = constants.ACCOUNT_SID
	auth_token = constants.AUTH_TOKEN 
	client = TwilioRestClient(account_sid, auth_token)
	
	try:
		message = client.messages.create(to="+1{}".format(constants.GAUTAM_NUMBER), from_=constants.TWILIO_NUMBER,
                	                     body="Hey Gautam, there was an error that came up during the appointment reminder thing! Details: {}".format(details))
	except:
		print sys.exc_info()[0]
