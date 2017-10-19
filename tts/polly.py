# TODO : Move aws_key stuff into letsrobot.conf

import boto3
from subprocess import Popen, PIPE
import os
import random

# to satisfy both python 2 and 3, goes away if keys are in conf
try:
    import secret
except ImportError:
    import tts.secret as secret

client = None
polly = None
voices = [ 'Nicole', 'Russell', 'Amy', 'Brian', 'Emma', 'Raveena', 'Ivy', 'Joanna', 'Joey', 'Justin',
             'Kendra', 'Kimberly', 'Mathew', 'Salli', 'Geraint' ]             
users = {}
robot_voice = None
hw_num = None

def setup(robot_config):
    global client
    global polly
    global robot_voice
    global users
    global hw_num
    
    owner = robot_config.get('robot', 'owner')
    owner_voice = robot_config.get('polly', 'owner_voice')
    robot_voice = robot_config.get('polly', 'robot_voice')
    hw_num = robot_config.getint('tts', 'hw_num')
    
    client = boto3.Session(aws_access_key_id=secret.aws_Key,
                            aws_secret_access_key=secret.aws_Secret,
                            region_name=secret.aws_Region)

    polly = boto3.client('polly', aws_access_key_id=secret.aws_Key,
                            aws_secret_access_key=secret.aws_Secret,
                            region_name=secret.aws_Region)
                            
    users[owner] = owner_voice
    
def say(message, *args):
    if (len(args) == 0): # simple say
        response = polly.synthesize_speech(
            OutputFormat = 'mp3',
            VoiceId = robot_voice,
            Text = message,
        )
    else:
        user = args[0]['name']

        if (args[0]['anonymous'] == True):
            voice = 'Mizuki'
        else:
            if user not in users:
                users[user] = random.choice(voices)
            voice = users[user]    
    
        rawMessage = args[0]['message']
        withoutName = rawMessage.split(']')[1:]
        message = "".join(withoutName)

        print(user + " voice " + voice + ": " + message)
    
        response = polly.synthesize_speech(
            OutputFormat = 'mp3',
            VoiceId = voice,
            Text = message,
        )

    if "AudioStream" in response:
#        out = open ('/tmp/polly.mp3', 'w+')
#        out.write(response['AudioStream'].read())
#        out.close()
#        player = Popen(['/usr/bin/mpg123-alsa', '-a', 'hw:1,1', '-q', '/tmp/polly.mp3'], stdin=PIPE, bufsize=1)
#        os.remove('/tmp/polly.mp3')
        play = Popen(['/usr/bin/mpg123-alsa', '-a', 'hw:%d,0' % hw_num, '-q', '-'], stdin=PIPE, bufsize=1)
        play.communicate(response['AudioStream'].read())

