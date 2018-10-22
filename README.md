# surveymonkey-python
Python wrapper for SurveyMonkey API

## Installing
```
pip install surveymonkey-python
```

## Usage

- Instantiate client
from client import Client
`# If you do not have access_token, run`
```
client=Client(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, access_token=None)
```
`If you have access_token, run`
```
client=Client(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, access_token=ACCESS_TOKEN)
```

- OAuth (instantiate client with  `access_token = None`)
1- Get authorization URL `client.get_authorization_url()`
2- Extract `code` from the URL and send it as an argument in `client.exchange_code(code)`
3- Remove the token from the response obtained and send it as an argument in `client.set_access_token(token)`

-Functionality methods, they refer to methods that make calls to the different endpoints of the SurveyMonkey API,
the use is quite simple:
`client.method(args)`
e.g. `client.get_survey_pages(survey_id)`
where `survey_id` represent the id of the survey.

# TODO
- Response Counts and Trends endpoints
- Contacts and Contact Lists endpoints
- Translations for Multilingual Surveys endpoints
- Collectors and Invite Messages endpoints
- Benchmarks endpoints
- Organizations endpoint
- Errors endpoint
