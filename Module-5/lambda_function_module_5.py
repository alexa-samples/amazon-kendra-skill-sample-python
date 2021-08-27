# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import boto3 

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard, AskForPermissionsConsentCard

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

PERMISSIONS = ['alexa::profile:given_name:read', 'alexa::profile:email:read']


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to Doc Support. What can I help you with?" 
        reprompt_output = "You can ask me about AWS documentation." # update according to your Amazon Kendra index
        
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["LastQuery"] = "no previous query"
        session_attr["QueryStatus"] = "none asked"
        session_attr["QueryCount"] = 0
        session_attr["LastOutput"] = speak_output
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_output)
                .response
        )


class CaptureQueryIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CaptureQueryIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        last_query = session_attr["LastQuery"]

        slots = handler_input.request_envelope.request.intent.slots
        if session_attr["QueryStatus"] == "asked not answered":
            query = last_query
        elif session_attr["QueryStatus"] == "new query":
            query = None
        else:
            query = slots["query"].value
            
        if query != last_query:
            session_attr["QueryCount"] = 0
            session_attr["QueryStatus"] = "new ask"
        
        if (session_attr["QueryStatus"] == "asked and answered" or query is None):
            speak_output = "You just asked about" + " " + last_query + ". What are you looking for now?"
            session_attr["QueryStatus"] = "new ask"
            session_attr["LastOutput"] = speak_output
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .response
            )

        if session_attr["QueryCount"] > 2:
            speak_output = "I'm having trouble finding information on your question. Please try asking it another way."
            session_attr["QueryCount"] = 0
            session_attr["QueryStatus"] = "new ask"
            session_attr["LastOutput"] = speak_output
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .response
            )
        
        index_id = 'indexID' # replace with your index ID
        
        sts_client = boto3.client('sts')
        assumed_role_object=sts_client.assume_role(RoleArn="<Your AWS resource role ARN>", RoleSessionName="AssumeRoleSession1") # replace with your AWS resource role ARN
        credentials=assumed_role_object['Credentials']
        
        kendra = boto3.client('kendra', 
                        aws_access_key_id=credentials['AccessKeyId'],
                        aws_secret_access_key=credentials['SecretAccessKey'],
                        aws_session_token=credentials['SessionToken'],
                        region_name='us-east-1') # replace with your index region name

        response = kendra.query(
            QueryText = query,
            IndexId = index_id)
            
        for query_result in response['ResultItems']:
            
            source_uri = query_result['DocumentURI']
            
            if session_attr["QueryStatus"] == "asked not answered": 
                session_attr["QueryStatus"] = "new pass"
                session_attr["QueryCount"] += 1
                continue
                   
            if session_attr["QueryCount"] == 2:
                session_attr["QueryCount"] += 1
                continue
            
            if (query_result['Type']=='ANSWER' or query_result['Type']=='QUESTION_ANSWER'): # optionally add QUESTION_ANSWER type
                answer_text = query_result['DocumentExcerpt']['Text']
                session_attr["QueryResult"] = answer_text
                speak_output = "I found this: " + answer_text + ". Is this what you were looking for?"    
                break
                
            if query_result['Type']=='DOCUMENT':
                document_text = query_result['DocumentExcerpt']['Text']
                session_attr["LastDocText"] = document_text
                if 'DocumentTitle' in query_result:
                    document_title = query_result['DocumentTitle']['Text']
                    session_attr["QueryResult"] = document_title
                    speak_output = "I found a document titled " + document_title + ". Is this what you were looking for? If you're not sure, you can say 'read me an excerpt'."
                else:
                    session_attr["QueryResult"] = document_text
                    speak_output = "I found this: " + document_text + ". Is this what you were looking for?"
                break
        
        session_attr["LastQuery"] = query
        session_attr["LastSourceURI"] = source_uri
        session_attr["LastHandler"] = "capture query"
        session_attr["LastOutput"] = speak_output
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class ReadDocIntentHandler(AbstractRequestHandler):
    """Handler for sending an email"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ReadDocIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        
        doc_text = session_attr["LastDocText"]
        
        speak_output = ('Here is an excerpt from the document:'
            '<audio src="soundbank://soundlibrary/musical/amzn_sfx_electronic_beep_03"/>' + doc_text + '.' 
            '<audio src="soundbank://soundlibrary/musical/amzn_sfx_electronic_beep_03"/>'
            'Is this what you were looking for?')
        
        session_attr["LastHandler"] = "read doc"
        session_attr["LastOutput"] = speak_output
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SendEmailIntentHandler(AbstractRequestHandler):
    """Handler for sending an email"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SendEmailIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        last_query = session_attr["LastQuery"]
        query_result = session_attr["QueryResult"]
        source_uri = session_attr["LastSourceURI"]
        
        service_client = handler_input.service_client_factory.get_ups_service()
        
        try:
            email = service_client.get_profile_email() 
            name = service_client.get_profile_given_name() 
        except:
            session_attr["LastOutput"] = "Please enable first name and email permissions in the Amazon Alexa app."
            return (
                handler_input.response_builder
                    .speak("Please enable first name and email permissions in the Amazon Alexa app.")
                    .set_card(AskForPermissionsConsentCard(permissions=PERMISSIONS))
                    .response
            )
        
        sts_client = boto3.client('sts')
        assumed_role_object=sts_client.assume_role(RoleArn="<Your AWS resource role ARN>", RoleSessionName="AssumeRoleSession2") # replace with your AWS resource role ARN
        credentials=assumed_role_object['Credentials']
                
        sns = boto3.client('sns',
                        aws_access_key_id=credentials['AccessKeyId'],
                        aws_secret_access_key=credentials['SecretAccessKey'],
                        aws_session_token=credentials['SessionToken'])
        
        user_id = handler_input.request_envelope.context.system.user.user_id
        
        topic_arn_response = sns.create_topic(Name='DocSupportSNS')
        topic_arn = topic_arn_response['TopicArn']
        
        try:
            sub_list = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
            sub_topic_arn = None
            while sub_topic_arn is None:
                for sub in sub_list['Subscriptions']:
                    sub_arn = sub['SubscriptionArn']
                    sub_attr = sns.get_subscription_attributes(SubscriptionArn=sub_arn)
                    if sub_attr['Attributes']['FilterPolicy'] == '{"user_id": ["' + user_id + '"]}':
                        sub_topic_arn = sub_attr['Attributes']['TopicArn']
                        break
                try:
                    sub_list = sns.list_subscriptions_by_topic(TopicArn=sub_list['NextToken'])
                except:
                    break
            
            sns.publish(
                TopicArn=sub_topic_arn,
                Subject='You asked about ' + last_query,
                Message=('Hi ' + name + ',\n' + 'You asked Doc Support about ' + last_query + '.' 
                        ' We found this: \n' + query_result +'\n' 
                        'More information can be found in the following documentation: ' + source_uri + ''),
                MessageAttributes={
                    'user_id':{
                        'DataType': 'String',
                        'StringValue': user_id
                    }
                }
            )
                
        except:
            filter_policy = '{"user_id": ["' + user_id + '"]}'
            
            sub_response = sns.subscribe(
                            TopicArn=topic_arn,
                            Protocol='email',
                            Endpoint=email,
                            Attributes={
                                'FilterPolicy': filter_policy}
                            )
            sub_status = sub_response["SubscriptionArn"]
                        
            if sub_status == 'pending confirmation':
                speak_output = ("Please check your inbox and confirm your subscription to the topic." 
                                "You will only receive emails when you request them from Doc Support." 
                                "Once you've confirmed, say 'send my email', or come back later and ask your question again.")
                session_attr["LastOutput"] = speak_output
                return (
                    handler_input.response_builder
                        .speak(speak_output)
                        .response
                )
        
        speak_output = "Ok. I'm sending you an email with the documentation about your query, " + last_query + ". Would you like to ask something else?"
        session_attr["LastHandler"] = "email"
        session_attr["LastOutput"] = speak_output
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class YesNoIntentHandler(AbstractRequestHandler):
    """Handler for Yes or No Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        
        yes = ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
        no = ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
        
        if (yes and (session_attr["LastHandler"] == "capture query" or session_attr["LastHandler"] == "read doc")): 
            speak_output = "Great. I can email you the document or you can ask another question. Which would you like?" 
            session_attr["QueryStatus"] = "asked and answered"
            session_attr["QueryCount"] = 0
            session_attr["LastOutput"] = speak_output
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .response
            )
                    
        if (no and (session_attr["LastHandler"] == "capture query" or session_attr["LastHandler"] == "read doc")): 
            session_attr["QueryStatus"] = "asked not answered"
            return CaptureQueryIntentHandler().handle(handler_input)
        
        if (yes and session_attr["LastHandler"] == "email"): 
            session_attr["QueryStatus"] = "new query"
            return CaptureQueryIntentHandler().handle(handler_input)
        
        if (no and session_attr["LastHandler"] == "email"):
            speak_output = "Ok. Goodbye!"
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .set_should_end_session(True)
                    .response
            )


class RepeatIntentHandler(AbstractRequestHandler):
    """Handler for Repeat Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.RepeatIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        speak_output = session_attr["LastOutput"]
        
        return (
                handler_input.response_builder
                    .speak(speak_output)
                    .response
            )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can ask me about AWS documentation. How can I help?" # update according to your Amazon Kendra index
        session_attr["LastOutput"] = speak_output

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can ask about AWS documentation. What would you like to do?" # update according to your Amazon Kendra index
        reprompt = "I didn't catch that. What can I help you with?"
        session_attr["LastOutput"] = speech

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = CustomSkillBuilder(api_client=DefaultApiClient())

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CaptureQueryIntentHandler())
sb.add_request_handler(ReadDocIntentHandler())
sb.add_request_handler(SendEmailIntentHandler())
sb.add_request_handler(YesNoIntentHandler())
sb.add_request_handler(RepeatIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
