
# https://football.fantasysports.yahoo.com/f1/756505/matchup?week=1&mid1=1

# https://football.fantasysports.yahoo.com/f1/756505/matchup?week=1&mid1=3&mid2=9
# 1 me
# 2 trevor
# 3 david
# 4 scott
# 5 catherine
# 6 chris
# 7 vince
# 8 tony
# 9 jambach
# 10 gannon

import json
import time
import webbrowser
import pandas as pd
from pandas.io.json import json_normalize
from rauth import OAuth1Service, OAuth2Service
from rauth.utils import parse_utf8_qsl

league_id = 756505

teams = {}

teams[1] = [1,3,4,5,6]
teams[2] = [1,2,4,5,6]
teams[3] = [1,2,5,6,7]
teams[4] = [1,2,3,6,7]
teams[5] = [1,2,3,7,8]
teams[6] = [1,2,3,4,8]
teams[7] = [1,2,3,4,9]
teams[8] = [1,2,3,4,5]
teams[9] = [1,2,3,4,5]
teams[10] = [1,3,4,5,6]
teams[11] = [1,2,4,5,6]
teams[12] = [1,2,5,6,7]
teams[13] = [1,2,3,6,7]
teams[14] = [1,2,3,7,8]
teams[15] = [3,5,1,4]
teams[16] = [3,1,6,9]

for week in range(16):
	for team in teams[week + 1]:
		webbrowser.open('https://football.fantasysports.yahoo.com/f1/756505/matchup?week={}&mid1={}'.format(week+ 1, team))

exit()

#Load Credentials
#Load a json file which has my consumer key and consumer secret.

#credentials_file = open('oauth.json')
#credentials = json.load(credentials_file)
#credentials_file.close()

credentials = {}
credentials['client_id'] = 'dj0yJmk9eldRRnhpcjFIMXBmJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTg4'
credentials['client_secret'] = 'ca455c34fd8627b6afd52ba92ba85f0ca8d2e959'

#Create OAuth Object
#OAuth object is used for the three-legged authentication required by the Yahoo API.

# oauth = OAuth1Service(consumer_key = credentials['consumer_key'],
#                       consumer_secret = credentials['consumer_secret'],
#                       name = "yahoo",
#                       request_token_url = "https://api.login.yahoo.com/oauth/v2/get_request_token",
#                       access_token_url = "https://api.login.yahoo.com/oauth/v2/get_token",
#                       authorize_url = "https://api.login.yahoo.com/oauth/v2/request_auth",
#                       base_url = "http://fantasysports.yahooapis.com/")

oauth = OAuth2Service(
    client_id=credentials['client_id'],
    client_secret=credentials['client_secret'],
    name='yahoo',
	access_token_url = "https://api.login.yahoo.com/oauth/v2/get_token",
	authorize_url = "https://api.login.yahoo.com/oauth/v2/request_auth",
	base_url = "http://fantasysports.yahooapis.com/")

redirect_uri = 'http://www.yahoo.com/'
params = {
	'client_id': credentials['client_id'],
	'response_type': 'id_token',
	'redirect_uri': 'oob',
	'nonce': '0UWdCWGx0QlEa0Y29uc3V',
	'scope': 'openid,fspt-r',
	'prompt': 'consent'
}
#	'response_type': 'code',
#	'scope': 'read_stream',

# get url for user auth
url = oauth.get_authorize_url(**params)
print(url)
exit()

# returns
# https://api.login.yahoo.com/oauth/v2/request_auth?client_id=dj0yJmk9eldRRnhpcjFIMXBmJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTg4&response_type=id_token&redirect_uri=oob&nonce=0UWdCWGx0QlEa0Y29uc3V&scope=openid%2Cfspt-r&prompt=consent
# which is NO GOOD
# this works (not sure where i got it from...)
# https://api.login.yahoo.com/oauth2/request_auth?client_id=dj0yJmk9eldRRnhpcjFIMXBmJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTg4&redirect_uri=oob&response_type=code&language=en-us
# and thus 
# https://api.login.yahoo.com/oauth2/request_auth?client_id=dj0yJmk9eldRRnhpcjFIMXBmJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTg4&redirect_uri=oob&response_type=code
# CODE: 7rc5euv
# token (broken):
# https://api.login.yahoo.com/oauth2/request_auth?client_id=dj0yJmk9eldRRnhpcjFIMXBmJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTg4&redirect_uri=http://www.yahoo.com&response_type=token

#https://api.login.yahoo.com/oauth2/request_auth?client_id=dj0yJmk9eldRRnhpcjFIMXBmJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTg4&redirect_uri=http://www.example.com&response_type=token&language=en-us

#webbrowser.open(url)

auth_code = "7rc5euv"
auth_code = "kpa6jvv"

session = oauth.get_auth_session(data={'code': auth_code,
	'redirect_uri': redirect_uri})
print(session)

# request_token, request_token_secret = oauth.get_request_token(params={"oauth_callback": "oob"})
# print(request_token, request_token_secret)

#Leg 2
#Obtain authorization to access protected resources. We do this by generating the auth url, opening it in our default web browser, and entering the verification code displayed.

#authorize_url = oauth.get_authorize_url(request_token)
#webbrowser.open(authorize_url)
#verify = input('Enter code: ')
#Enter code: k2pm8y


# Leg 3
# Obtain access tokens. Tokens expire after 3600 seconds (60 minutes) 
# so we'd like to save the time these tokens were generated. This time can be 
# used later to check against and refresh the tokens if necessary. 
# Next, we'll also save the tokens in our credentials dictionary and create a tuple that is used in the creation of a session

raw_access = oauth.get_raw_access_token(request_token,
                                        request_token_secret,
                                        params={"oauth_verifier": verify})

parsed_access_token = parse_utf8_qsl(raw_access.content)
access_token = (parsed_access_token['oauth_token'], parsed_access_token['oauth_token_secret'])

start_time = time.time()
end_time = start_time + 3600

credentials['access_token'] = parsed_access_token['oauth_token']
credentials['access_token_secret'] = parsed_access_token['oauth_token_secret']
tokens = (credentials['access_token'], credentials['access_token_secret'])

#Start a session

s = oauth.get_session(tokens)

#Send a query
#Query the api and receive output in json format. The Yahoo Fantasy Sports API guide explains how queries are created.

url = 'http://fantasysports.yahooapis.com/fantasy/v2/leagues;league_keys=nfl.l.427049'
r = s.get(url, params={'format': 'json'})
r.status_code
