# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import boto3 

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
        else:
            query = slots["query"].value
            
        if query != last_query:
            session_attr["QueryCount"] = 0
            session_attr["QueryStatus"] = "new ask"
        
        if (session_attr["QueryStatus"] == "asked and answered" or query is None):
            speak_output = "You just asked about" + " " + last_query + ". What are you looking for now?"
            session_attr["QueryStatus"] = "new ask"
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .response
            )

        if session_attr["QueryCount"] > 2:
            speak_output = "I'm having trouble finding information on your question. Please try asking it another way."
            session_attr["QueryCount"] = 0
            session_attr["QueryStatus"] = "new ask"
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
            
            if session_attr["QueryStatus"] == "asked not answered": 
                session_attr["QueryStatus"] = "new pass"
                session_attr["QueryCount"] += 1
                continue
                   
            if session_attr["QueryCount"] == 2:
                session_attr["QueryCount"] += 1
                continue
            
            if (query_result['Type']=='ANSWER' or query_result['Type']=='QUESTION_ANSWER'): # optionally add QUESTION_ANSWER type
                answer_text = query_result['DocumentExcerpt']['Text']
                speak_output = "I found this: " + answer_text + ". Is this what you were looking for?"    
                break
                
            if query_result['Type']=='DOCUMENT':
                document_text = query_result['DocumentExcerpt']['Text']
                if 'DocumentTitle' in query_result:
                    document_title = query_result['DocumentTitle']['Text']
                    speak_output = "I found a document titled " + document_title + ". Is this what you were looking for?"  
                else:
                    speak_output = "I found this: " + document_text + ". Is this what you were looking for?"
                break
        
        session_attr["LastQuery"] = query
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
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
        
        if yes:
            speak_output = "Great. If you have another question, you can say 'ask another question'."
            session_attr["QueryStatus"] = "asked and answered"
            session_attr["QueryCount"] = 0
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .response
            )
                    
        if no:
            session_attr["QueryStatus"] = "asked not answered"
            return CaptureQueryIntentHandler().handle(handler_input)


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

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
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

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


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CaptureQueryIntentHandler())
sb.add_request_handler(YesNoIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
