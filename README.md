In order to help my mom out with appointment reminders at her Kumon center, I built this program to send text reminders to her appointments the day before. It uses
Twilio for sending the text reminders, and pulls from her Google Calendar in order to gather the appointment information. On my server at home, I have this setup
as a Cron Job that runs at 3:00 PM EST every day. The general breakdown of the files is as follows.

*appointmentReminderCronJob.py - Code that accesses the users Google Calendar and parses the events in order to figure out what text messages to send and to who.
*sendReminder.py - Code that corresponds with Twilio to send the actual texts
*oauthTokens.db - Database that holds the necessary OAuth information on the user
*constants.py - A file that holds all the constants for the program
*appointmentRemdinderScript.sh - The actual bash script that is run as a CronJob every day.
*appointmentLogs.txt - File that holds the logs resulting from the program running everyday.
*requirements.txt - Python modules downloaded via 'pip' to run program. Note: I use this virtualenv for multiple projects, therefore this file is longer then necessary

Note: Access to Google Calendar requires OAUTH2 support. I have a separate set of code, not included here, that deals with requesting permission from the user to grab
the necessary tokens and store these in the SQLite database. This code assumes that part is already taken care of and stored inside the oauthTokens.db file.
