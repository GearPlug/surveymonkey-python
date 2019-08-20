import json
import requests
from urllib.parse import urlencode

from surveymonkey.exceptions import UnknownError, BadRequestError, AuthorizationError, PermissionError, \
    ResourceNotFoundError, ResourceConflictError, RequestEntityTooLargeError, RateLimitReachedError, \
    InternalServerError, UserSoftDeletedError, UserDeletedError

'''
Token expiration and revocation
Our access tokens don’t currently expire but may in the future. We’ll warn all developers before making changes.

Access tokens can be revoked by the user. If this happens, you’ll get a JSON-encoded response body including a key 
statuswith a value of 1 and a key errmsg with the value of Client revoked access grant when making an API request. 
If you get this response, you’ll need to complete OAuth again.
'''

BASE_URL = "https://api.surveymonkey.com"
API_URL = "https://api.surveymonkey.com/v3"
AUTH_CODE = "/oauth/authorize"
ACCESS_TOKEN_URL = "/oauth/token"


class Client(object):

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, access_token=None):
        self.code = None
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.client_secret = client_secret
        self._access_token = access_token

    # Authorization
    def get_authorization_url(self):
        """

        :return:
        """
        params = {'client_id': self.client_id, 'redirect_uri': self.redirect_uri, 'response_type': 'code'}
        url = BASE_URL + AUTH_CODE + '?' + urlencode(params)
        return url

    def exchange_code(self, code):
        """

        :param code:
        :return:
        """
        params = {'code': code, 'client_id': self.client_id, 'client_secret': self.client_secret,
                  'redirect_uri': self.redirect_uri, 'grant_type': 'authorization_code'}
        url = BASE_URL + ACCESS_TOKEN_URL
        response = requests.post(url, data=params)
        if response.status_code == 200 and 'access_token' in response.text:
            return response.text
        else:
            return False

    def refresh_token(self):
        """
        not implemented yet, but may in the future
        :return:
        """
        pass

    def set_access_token(self, token):
        """

        :param token:
        :return:
        """
        if isinstance(token, dict):
            self._access_token = token['access_token']
        else:
            self._access_token = token

    # Functionality
    def get_authenticated_user(self):
        """
        Returns the current user’s account details including their plan.
        :return:
        """
        endpoint = "/users/me"
        url = API_URL + endpoint
        return self._get(url)

    def get_user_workgroup(self, user_id):
        """
        Returns the workgroups that a specific user is in.
        :return:
        """
        endpoint = "/users/{0}/workgroups".format(user_id)
        url = API_URL + endpoint
        return self._get(url)

    def get_shared_resources_to_user(self, user_id):
        """
        Returns the resources shared with a user across all workgroups.
        :return:
        """
        endpoint = "/users/{user_id}/shared".format(user_id)
        url = API_URL + endpoint
        return self._get(url)

    def get_authenticated_user_group(self):
        """
        Returns a team if the user account belongs to a team (users can only belong to one team).
        :return:
        """
        endpoint = "/groups"
        url = API_URL + endpoint
        return self._get(url)

    def get_group_details(self, group_id):
        """
        Returns a teams’s details including the teams’s owner and email address.
        :param group_id: id of the group you want details from
        :return:
        """
        endpoint = "/groups/{0}".format(group_id)
        url = API_URL + endpoint
        return self._get(url)

    def get_group_members(self, group_id):
        """
        Returns a list of users who have been added as members of the specified group.
        :param group_id: id of the group you want details from
        :return:
        """
        endpoint = "/groups/{0}/members".format(group_id)
        url = API_URL + endpoint
        return self._get(url)

    def get_group_member_detail(self, group_id, member_id):
        """
        Returns a group member’s details including their role and status.
        :param group_id: id of the group you want details from
        :param member_id: id of member of the group you want details of
        :return:
        """
        endpoint = "/groups/{0}/members".format(group_id)
        url = API_URL + endpoint
        return self._get(url)

    def get_events_list(self):
        """
        List all possible events to subscribe
        :return:
        """
        return ["response_completed", "response_disqualified", "response_updated", "response_created",
                "response_deleted", "response_overquota", "survey_created", "survey_updated", "survey_deleted",
                "collector_created", "collector_updated", "collector_deleted", "app_installed", "app_uninstalled"]

    def get_webhooks_list(self):
        """
        List all create webhooks - subscribed events
        :return:
        """
        endpoint = "/webhooks"
        url = API_URL + endpoint
        return self._get(url)

    def create_webhook(self, survey_id, callback_uri, event, webhook_name, object_type):
        """
        Create webhook - subscribe to an event
        :return:
        """
        payload = {
            "name": webhook_name,
            "event_type": event,
            "object_type": object_type,
            "object_ids": survey_id,
            "subscription_url": callback_uri
        }
        endpoint = "/webhooks"
        url = API_URL + endpoint
        return self._post(url, json=payload)

    def delete_webhook(self, webhook_id):
        """
        Delete webhook - unsubscribe to an event
        :param webhook_id: id of specific webhook or subscription to delete.
        :return:
        """
        endpoint = '/webhooks/{0}'.format(webhook_id)
        url = API_URL + endpoint
        return self._delete(url)

    def get_survey_lists(self):
        """
        List all created surveys.
        :return:
        """
        endpoint = "/surveys"
        url = API_URL + endpoint
        return self._get(url)

    def get_specific_survey(self, survey_id):
        """
        Returns a survey’s details.
        :param survey_id: id of specific survey from which you want details
        :return:
        """
        endpoint = "/surveys/{}".format(survey_id)
        url = API_URL + endpoint
        return self._get(url)

    def modify_specific_survey(self, survey_id, **kwargs):
        """
         Modifies a survey’s title, nickname or language.
        :param survey_id: id of survey you want to modify
        :param kwargs:
            title, required: No (PUT default=“New Survey”), description: Survey title, type: String
            nickname, required: No (PUT default=“”), description: Survey nickname, type: String
            language, required: No (PUT default=“en”), description: Survey language, type: String
            buttons_text, required: No, description: Survey Buttons text container, type: Object
            buttons_text.next_button, required: No, description: Button text, type: String
            buttons_text.prev_button, required: No, description: Button text, type: String
            buttons_text.exit_button, required: No, description: Button text. If set to an empty string, button will
                be ommitted from survey, type: String
            buttons_text.done_button, required: No, description: Button text, type: String
            custom_variables, required: No, description: Dictionary of survey variables, type: Object
            footer, required: No (default=true), description: If false, SurveyMonkey’s footer is not displayed
                type: Boolean
            folder_id, required: No, description: If specified, adds the survey to the folder with that id.
                type: String
        :return:
        """
        endpoint = "/surveys/{}".format(survey_id)
        url = API_URL + endpoint
        return self._patch(url, json=kwargs)

    def delete_survey(self, survey_id):
        """
        Deletes a survey.
        :param survey_id: id of survey you want to delete
        :return:
        """
        endpoint = "/surveys/{}".format(survey_id)
        url = API_URL + endpoint
        return self._delete(url)

    def get_survey_details(self, survey_id):
        """
        Details of a specific survey
        :param survey_id: id of specific survey to get details from
        :return:
        """
        endpoint = "/surveys/{0}/details".format(survey_id)
        url = API_URL + endpoint
        return self._get(url)

    def get_survey_categories(self):
        """
        Returns a list of survey categories that can be used to filter survey templates.
        :return:
        """
        endpoint = "/survey_categories"
        url = API_URL + endpoint
        return self._get(url)

    def get_survey_templates(self):
        """
        Returns a list of survey templates. Survey template ids can be used as an argument to POST a new survey.
        :return:
        NOTE: for Teams -- Shared Team templates are not available through the API at this time.
            This endpoint returns SurveyMonkey’s template list.
        """
        endpoint = "/survey_templates"
        url = API_URL + endpoint
        return self._get(url)

    def get_survey_languages(self):
        """
        Returns a list of survey languages that can be used to generate translations for multilingual surveys
        :return:
        """
        endpoint = "/survey_languages"
        url = API_URL + endpoint
        return self._get(url)

    def get_survey_pages(self, survey_id):
        """
        Returns a survey page’s.
        :param survey_id: id of survey you want page's details
        :return:
        """
        endpoint = "/surveys/{}/pages".format(survey_id)
        url = API_URL + endpoint
        return self._get(url)

    def create_new_empty_survey_page(self, survey_id, **kwags):
        """
        Creates a new, empty page
        :param survey_id: id of survey you want page's details
        :param kwargs: dictionary with the following data
            title, required: No (default=“”), description: Page title, type: String
            description, required: No (default: “”), description: Page description, type: String
            position, required: No (default=end), description: Position of page in survey, type: Integer
        :return:
        """
        endpoint = "/surveys/{}/pages".format(survey_id)
        url = API_URL + endpoint
        return self._post(url, json=kwags)

    def get_survey_page_details(self, survey_id, page_id):
        """
        Returns a page’s details.
        :param survey_id: id of survey you want page's details
        :param page_id: id of page from which you want details
        :return:
        """
        endpoint = "/surveys/{0}/pages/{1}".format(survey_id, page_id)
        url = API_URL + endpoint
        return self._get(url)

    def modify_survey_page(self, survey_id, page_id, **kwargs):
        """
        Modifies a page (updates any fields accepted as arguments to POST /surveys{id}/pages).
        :param survey_id: id of page's survey
        :param page_id: id of page you want to modify or edit
        :param kwargs: dictionary with the following data
            title, required: No (default=“”), description: Page title, type: String
            description, required: No (default: “”), description: Page description, type: String
            position, required: No (default=end), description: Position of page in survey, type: Integer
        :return:
        """
        endpoint = "/surveys/{0}/pages/{1}".format(survey_id, page_id)
        url = API_URL + endpoint
        return self._patch(url, json=kwargs)

    def delete_survey_page(self, survey_id, page_id):
        """
        Deletes a page.
        :param survey_id: id of page's survey
        :param page_id: id of page you want to delete
        :return:
        """
        endpoint = "/surveys/{0}/pages/{1}".format(survey_id, page_id)
        url = API_URL + endpoint
        return self._delete(url)

    def get_survey_page_questions(self, survey_id, page_id):
        """
        Returns a list of questions on a survey page.
        :param survey_id: id of page's survey
        :param page_id: id of page you want to get the questions
        :return:
        """
        endpoint = "/surveys/{0}/pages/{1}/questions".format(survey_id, page_id)
        url = API_URL + endpoint
        return self._get(url)

    def create_survey_page_question(self, survey_id, page_id, **kwargs):
        """
        Creates a new question on a survey page.
        :param survey_id: id of page's survey
        :param page_id: id of page where you want to create the questions
        :param kwargs: dictionary with the following data
        title, required: No (default=“”), description: Page title, type: String
            headings, required: Yes, description:List of question headings objects, type: Array
            headings[_].heading, required: Yes, description:The title of the question, or empty string if
                random_assignment is defined, type: String
            headings[_].description, required: No, description:If random_assignment is defined, and family is
                presentation_image this is the title, type: String
            headings[_].image, required: No, description:Image data when question family is presentation_image,
                type: Object or null
            headings[_].image.url, required: No, description:URL of image when question family is presentation_image,
                type: String
            headings[_].random_assignment, required: No, description: Random assignment data, type: Object or null
            headings[_].random_assignment.percent, required: Yes, description: Percent chance of this random assignment
                showing up (must sum to 100), type: Integer
            headings[_].random_assignment.position, required: No, description: Position of the random_assignment in
                survey creation page, type: Integer
            headings[_].random_assignment.variable_name, required: No, description: Internal use name for question
                tracking, can be "", type: String
            position, required: No (default=last), description: Position of question on page, type: Integer
            family, required: Yes, description: Question family determines the type of question, see formatting
                question types, type: String
            subtype, required: Yes, description: Question family’s subtype further specifies the type of question,
                see formatting question types, type: String
            sorting, required: No, description:Sorting details of answers, type: Object
            sorting.type, required: Yes, description:Sort answer choices by: default, textasc, textdesc,
                resp_count_asc, resp_count_desc, random, flip, type: String-ENUM
            sorting.ignore_last, required: No, description:If true, does not sort the last answer option
                (useful for “none of the above”, etc), type: Boolean
            required, required: No, description: Whether an answer is required for this question, type: Object
            required.text, required: Yes, description: Text to display if a required question is not answered,
                type: String
            required.type, required: Yes if question is matrix_single, matrix_ranking, and matrix menu,
                description: Specifies how much of the question must be answered: all , at_least, at_most, exactly,
                or range, type: String-ENUM
            required.amount, required: Yes if type is defined, description: The amount of answers required to be
                answered. If the required type is range then this is two numbers separated by a comma, as a string
                (e.g. “1,3” to represent the range of 1 to 3) String validation, required: No,
                description: Whether the answer must pass certain validation parameters, type: Object
            validation.type, required: Yes, description: Type of validation to use: any, integer, decimal,
                date_us, date_intl, regex, email, or text_length, type: String-ENUM
            validation.text, required: Yes, description:Text to display if validation fails	String
            validation.min, required: Yes, description: Minimum value an answer can be to pass validation,
                type: Date string, integer, or null depending on validation.type
            validation.max, required: Yes, description: Maximum value an answer can be to pass validation,
                type: Date string, integer, or null depending on validation.type
            validation.sum, required: No, description: Only accepted is family=open_ended and subtype=numerical,
                the exact integer textboxes must sum to in order to pass validation, type: Integer
            validation.sum_text, required: No, description: Only accepted is family=open_ended and subtype=numerical,
                the message to display if textboxes do not sum to validation.sum, type: String
            forced_ranking, required: No, description: Required if type is matrix and subtype is rating or single,
                whether or not to force ranking, type: Boolean
            quiz_options, required: No, description: Object containing the quiz properties of this question,
                if quiz-mode is enabled
            quiz_options.scoring_enabled, required: Yes, description: Whether this question is quiz-enabled,
                type: Boolean
            quiz_options.feedback, required: Yes, description: Object containing the definitions for feedback on
                this quiz question, type: Object
            quiz_options.feedback.correct_text, required: Yes, description: Text to show when answer is correct,
                type: String
            quiz_options.feedback.incorrect_text, required: Yes, description: Text to show when the ansewr is
                incorrect, type: String
            quiz_options.feedback.partial_text, required: Yes, description: Text to show when the answer is
                partially correct, type: String
            answers, required: Yes for all question types except open_ended_single, description: Answers object,
                refer to Formatting Question Types, type: Object
            display_options, required: Yes for File Upload, Slider, Image Choice, & Emoji/Star Rating question types,
                description: Display option object, refer to Formatting Question Types, type: Object
        :return:
        """
        endpoint = "/surveys/{0}/pages/{1}/questions".format(survey_id, page_id)
        url = API_URL + endpoint
        return self._post(url, json=kwargs)

    def get_specific_question(self, survey_id, page_id, question_id):
        """
        Returns a question.
        :param survey_id: id of survey
        :param page_id: id of page
        :param question_id: id of question
        :return:
        """
        endpoint = "/surveys/{0}/pages/{1}/questions/{2}".format(survey_id, page_id, question_id)
        url = API_URL + endpoint
        return self._get(url)

    def modify_specific_question(self, survey_id, page_id, question_id, **kwargs):
        """

        :param survey_id: id of survey
        :param page_id: id of page
        :param question_id: id of question
        :param kwargs: dictionary with the following data
        title, required: No (default=“”), description: Page title, type: String
            headings, required: Yes, description:List of question headings objects, type: Array
            headings[_].heading, required: Yes, description:The title of the question, or empty string if
                random_assignment is defined, type: String
            headings[_].description, required: No, description:If random_assignment is defined, and family is
                presentation_image this is the title, type: String
            headings[_].image, required: No, description:Image data when question family is presentation_image,
                type: Object or null
            headings[_].image.url, required: No, description:URL of image when question family is presentation_image,
                type: String
            headings[_].random_assignment, required: No, description: Random assignment data, type: Object or null
            headings[_].random_assignment.percent, required: Yes, description: Percent chance of this random assignment
                showing up (must sum to 100), type: Integer
            headings[_].random_assignment.position, required: No, description: Position of the random_assignment in
                survey creation page, type: Integer
            headings[_].random_assignment.variable_name, required: No, description: Internal use name for question
                tracking, can be "", type: String
            position, required: No (default=last), description: Position of question on page, type: Integer
            family, required: Yes, description: Question family determines the type of question, see formatting
                question types, type: String
            subtype, required: Yes, description: Question family’s subtype further specifies the type of question,
                see formatting question types, type: String
            sorting, required: No, description:Sorting details of answers, type: Object
            sorting.type, required: Yes, description:Sort answer choices by: default, textasc, textdesc,
                resp_count_asc, resp_count_desc, random, flip, type: String-ENUM
            sorting.ignore_last, required: No, description:If true, does not sort the last answer option
                (useful for “none of the above”, etc), type: Boolean
            required, required: No, description: Whether an answer is required for this question, type: Object
            required.text, required: Yes, description: Text to display if a required question is not answered,
                type: String
            required.type, required: Yes if question is matrix_single, matrix_ranking, and matrix menu,
                description: Specifies how much of the question must be answered: all , at_least, at_most, exactly,
                or range, type: String-ENUM
            required.amount, required: Yes if type is defined, description: The amount of answers required to be
                answered. If the required type is range then this is two numbers separated by a comma, as a string
                (e.g. “1,3” to represent the range of 1 to 3) String validation, required: No,
                description: Whether the answer must pass certain validation parameters, type: Object
            validation.type, required: Yes, description: Type of validation to use: any, integer, decimal,
                date_us, date_intl, regex, email, or text_length, type: String-ENUM
            validation.text, required: Yes, description:Text to display if validation fails	String
            validation.min, required: Yes, description: Minimum value an answer can be to pass validation,
                type: Date string, integer, or null depending on validation.type
            validation.max, required: Yes, description: Maximum value an answer can be to pass validation,
                type: Date string, integer, or null depending on validation.type
            validation.sum, required: No, description: Only accepted is family=open_ended and subtype=numerical,
                the exact integer textboxes must sum to in order to pass validation, type: Integer
            validation.sum_text, required: No, description: Only accepted is family=open_ended and subtype=numerical,
                the message to display if textboxes do not sum to validation.sum, type: String
            forced_ranking, required: No, description: Required if type is matrix and subtype is rating or single,
                whether or not to force ranking, type: Boolean
            quiz_options, required: No, description: Object containing the quiz properties of this question,
                if quiz-mode is enabled
            quiz_options.scoring_enabled, required: Yes, description: Whether this question is quiz-enabled,
                type: Boolean
            quiz_options.feedback, required: Yes, description: Object containing the definitions for feedback on
                this quiz question, type: Object
            quiz_options.feedback.correct_text, required: Yes, description: Text to show when answer is correct,
                type: String
            quiz_options.feedback.incorrect_text, required: Yes, description: Text to show when the ansewr is
                incorrect, type: String
            quiz_options.feedback.partial_text, required: Yes, description: Text to show when the answer is
                partially correct, type: String
            answers, required: Yes for all question types except open_ended_single, description: Answers object,
                refer to Formatting Question Types, type: Object
            display_options, required: Yes for File Upload, Slider, Image Choice, & Emoji/Star Rating question types,
                description: Display option object, refer to Formatting Question Types, type: Object
        :return:
        """
        endpoint = "/surveys/{0}/pages/{1}/questions/{2}".format(survey_id, page_id, question_id)
        url = API_URL + endpoint
        return self._patch(url, json=kwargs)

    def delete_question(self, survey_id, page_id, question_id):
        """
        Deletes a question.
        :param survey_id: id of survey
        :param page_id: id of page
        :param question_id: id of question
        :return:
        """
        endpoint = "/surveys/{0}/pages/{1}/questions/{2}".format(survey_id, page_id, question_id)
        url = API_URL + endpoint
        return self._delete(url)

    def get_questions_bank(self):
        """
        Get a list of questions that exist in the question bank
        :return:
        """
        endpoint = "/question_bank/questions"
        url = API_URL + endpoint
        return self._get(url)

    def get_survey_response(self, survey_id):
        """
        Returns a list of responses.
        :param survey_id: id of survey
        :return:
        """
        endpoint = "/surveys/{}/responses/".format(survey_id)
        url = API_URL + endpoint
        return self._get(url)

    def get_survey_response_bulk(self, survey_id):
        """
        Retrieves a list of full expanded responses, including answers to all questions.
        :param survey_id: id of survey
        :return:
        """
        endpoint = "/surveys/{}/responses/bulk".format(survey_id)
        url = API_URL + endpoint
        return self._get(url)

    def create_survey_from_template_or_existing_survey(self, title=None, template_id=None, survey_id=None):
        """
        Creates a new survey from a template using the template_id or existing survey using the survey_id
        :param title: Survey title, not required, String
        :param template_id: Survey template to copy from, not required, String
        :param survey_id: Survey id to copy from, not required, String
        :return:
        """
        payload = {
            "title": title,
            "from_template_id": template_id,
            "from_survey_id": survey_id
        }
        endpoint = "/surveys"
        url = API_URL + endpoint
        return self._post(url, json=payload)

    def create_new_blank_survey(self, **kwargs):
        """
        Creates a new empty survey
        :param kwargs: dictionary with the following data.
            title, required: No (default=“New Survey”), description: Survey title, type: String
            nickname, required: No (default=“”), description: Survey nickname, type: String
            language, required: No (default=“en”), description: Survey language, type: String
            buttons_text, required: No, description: Survey Buttons text container, type: Object
            buttons_text.next_button, required: No, description: Button text, type: String
            buttons_text.prev_button, required: No, description: Button text, type: String
            buttons_text.exit_button, required: No, description: Button text. If set to an empty string,
                button will be ommitted from survey, type: String
            buttons_text.done_button, required: No, description: Button text, type: String
            custom_variables, required: No, description: Dictionary of survey variables, type: Object
            footer, required: No (default=true), description: If false, SurveyMonkey’s footer is not displayed,
                type: Boolean
            folder_id, required: No, description: If specified, adds the survey to the folder with that id.	type: String
            quiz_options, required: No, description: An object describing the quiz settings, if this survey is a quiz
            	type: Object
            quiz_options.is_quiz_mode, required: Yes, description: On/off toggle for setting this survey as a quiz
                type: Boolean
            quiz_options.default_question_feedback, required: No, description: An object containing the default
                feedback for newly created questions in this survey, type: Object
            quiz_options.default_question_feedback.correct_text, required: Yes, description: Text to show when answer
                is correct, type: String
            quiz_options.default_question_feedback.incorrect_text, required: Yes, description: Text to show when answer
                is incorrect, type: String
            quiz_options.default_question_feedback.partial_text, required: Yes, description: Text to show when answer
                is partially correct, type: String
            quiz_options.show_results_type, required: Yes, description: What to reveal to the user when they complete
                the quiz: disabled, results_only or results_and_answers, type: String-ENUM
            quiz_options.feedback, required: Yes, description: Text to show the user when they complete the quiz
                type: Object
            quiz_options.feedback.ranges, required: Yes, description: The ranges at which to show users certain
                feedback, type: Array
            quiz_options.feedback.ranges_type, required: Yes, description: Configure whether the following parameters
                use percentage or points. Note that these ranges are inclusive and may not overlap, type: String-ENUM
            quiz_options.feedback.ranges[_].min, required: Yes, description: Minimum score for this feedback,
                type: Integer
            quiz_options.feedback.ranges[_].max, required: Yes, description: Maximum score for this feedback,
                type: Integer
            quiz_options.feedback.ranges[_].message, required: Yes, description: Feedback message, type: String
        :return:
        """
        endpoint = "/surveys"
        url = API_URL + endpoint
        return self._post(url, json=kwargs)

    def get_survey_folders(self):
        """
        Returns available folders
        :return:
        """
        endpoint = "/survey_folders"
        url = API_URL + endpoint
        return self._get(url)

    def create_survey_folder(self, **kwargs):
        """

        :param kwargs: diccionarion con los siguientes valores
            Title, required: No, description: Title for the folder, type: String
        :return:
        """
        endpoint = "/survey_folders"
        url = API_URL + endpoint
        return self._post(url, json=kwargs)

    def get_survey_translations(self, survey_id):
        """
        Returns all existing translations
        :param survey_id: id of survey
        :return:
        """
        endpoint = "/surveys/{0}/languages".format(survey_id)
        url = API_URL + endpoint
        return self._get(url)

    def get_responses(self, survey_id):
        """
        List all responses given to a specific survey.
        :param survey_id: id of specific survey to from
        :return:
        """
        endpoint = "/surveys/{0}/responses/".format(survey_id)
        url = API_URL + endpoint
        return self._get(url)

    def get_response_bulk(self, survey_id,params=None):
        """
        Retrieves a list of full expanded responses, including answers to all questions
        :param survey_id: id of survey to responses from
        :param params: a dict of params to add to the request, possible values can be 
                found at https://developer.surveymonkey.com/api/v3/#surveys-id-responses-bulk
        :return:
        """
        endpoint = "/surveys/{0}/responses/bulk".format(survey_id)

        url = API_URL + endpoint
        return self._get(url,params=params)

    def get_response_details(self, survey_id, response_id):
        """
        List answers of a survey given by an user.
        answers correspond to every question in a survey.
        response is survey completed by an user.
        :param survey_id: id of specific survey to get responses from
        :param response_id: id of specific response for a survey
        :return:

        """
        endpoint = "/surveys/{0}/responses/{1}/details".format(survey_id, response_id)
        url = API_URL + endpoint
        return self._get(url)

    # Communications
    def _get(self, endpoint, **kwargs):
        return self._request('GET', endpoint, **kwargs)

    def _post(self, endpoint, **kwargs):
        return self._request('POST', endpoint, **kwargs)

    def _put(self, endpoint, **kwargs):
        return self._request('PUT', endpoint, **kwargs)

    def _patch(self, endpoint, **kwargs):
        return self._request('PATCH', endpoint, **kwargs)

    def _delete(self, endpoint, **kwargs):
        return self._request('DELETE', endpoint, **kwargs)

    def _request(self, method, url, **kwargs):
        _headers = {"Authorization": "Bearer %s" % self._access_token, "Content-Type": "application/json"}
        return self._parse(requests.request(method, url, headers=_headers, **kwargs))

    def _parse(self, response):
        status_code = response.status_code
        if 'application/json' in response.headers['Content-Type']:
            r = response.json()
        else:
            r = response.text
        if "error" in r:
            self.get_error(dict(r))
        if "error" not in r and status_code not in [200, 201, 204]:
            raise UnknownError()
        if status_code in (200, 201):
            return r
        if status_code == 204:
            return None

    def get_error(self, error):
        """

        :return:
        """
        error_code = error['error']
        error_message = error['message']
        if error_code == "1000":
            raise BadRequestError(error_message)
        elif error_code == "1001":
            raise BadRequestError(error_message)
        elif error_code == "1002":
            raise BadRequestError(error_message)
        elif error_code == "1003":
            raise BadRequestError(error_message)
        elif error_code == "1004":
            raise BadRequestError(error_message)
        elif error_code == "1010":
            raise AuthorizationError(error_message)
        elif error_code == "1011":
            raise AuthorizationError(error_message)
        elif error_code == "1012":
            raise AuthorizationError(error_message)
        elif error_code == "1013":
            raise AuthorizationError(error_message)
        elif error_code == "1014":
            raise PermissionError(error_message)
        elif error_code == "1015":
            raise PermissionError(error_message)
        elif error_code == "1016":
            raise PermissionError(error_message)
        elif error_code == "1017":
            raise PermissionError(error_message)
        elif error_code == "1018":
            raise PermissionError(error_message)
        elif error_code == "1020":
            raise ResourceNotFoundError(error_message)
        elif error_code == "1025":
            raise ResourceConflictError(error_message)
        elif error_code == "1026":
            raise ResourceConflictError(error_message)
        elif error_code == "1030":
            raise RequestEntityTooLargeError(error_message)
        elif error_code == "1040":
            raise RateLimitReachedError(error_message)
        elif error_code == "1050":
            raise InternalServerError(error_message)
        elif error_code == "1051":
            raise InternalServerError(error_message)
        elif error_code == "1052":
            raise UserSoftDeletedError(error_message)
        elif error_code == "1053":
            raise UserDeletedError(error_message)
        else:
            raise UnknownError("UNKNOWN ERROR: {}".format(error['message']))
