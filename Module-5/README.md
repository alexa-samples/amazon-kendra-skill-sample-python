# Module 5: Improving user experience

If a user isn’t sure what to do, didn’t hear what Alexa said, or says something you haven’t equipped your skill for, you want to make sure Alexa handles the situation gracefully. These features will ensure the user’s requests are dealt with as seamlessly as possible. 

## RepeatIntentHandler

If the user didn’t catch what Alexa said or is confused when they hear it the first time, they might ask your skill to repeat what it said. Implement a handler for that request. 

1. On the **Build** page, add a new intent by choosing **Use an existing intent from Alexa's built-in library**. Find **AMAZON.RepeatIntent** and select **Add Intent**. Your Intents list should now include this built-in intent. 
2. Save and build your updated model.
3. Go back to the **Code** page. Find the **HelpIntentHandler**, create a new line above it, and copy and paste this code so it’s between **YesNoIntentHandler** and **HelpIntentHandler**.
```
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
                    .set_should_end_session(False)
                    .response
            )
```

When the user says something like “repeat that” or “say that again”, this handler will be triggered. 

4. In the code above, note the new session attribute, **LastOutput**. You need to add this session attribute to your other handlers to save your skill’s last output every time. 

Any place that your skill returns output to the user, add this line before the return line:
```
session_attr["LastOutput"] = speak_output
```

You *must* add this line above every return line that includes `.speak(speak_output)`, otherwise your skill’s most recent output might not be what gets repeated back to the user. 

Note that in **SendEmailIntentHandler**, there are several return lines that output speech without a `speak_output` variable. For those, either create a `speak_output` variable with the output speech and assign it to `session_attr["LastOutput"]`, or assign the same output speech text to `session_attr["LastOutput"]`, as seen below.
```
except:
    session_attr["LastOutput"] = "Please enable first name and email permissions in the Amazon Alexa app."
    return (
        handler_input.response_builder
            .speak("Please enable first name and email permissions in the Amazon Alexa app.")
            .set_card(AskForPermissionsConsentCard(permissions=PERMISSIONS))
            .response
    )
```
Similarly, don’t forget that there are several `speak_output` variables in **CaptureQueryIntentHandler** (in addition to those in **ReadDocIntentHandler** and **YesNoIntentHandler**) that should be saved in `session_attr["LastOutput"]`.

5. Register the handler at the bottom of the file. Paste this line below `sb.add_request_handler(YesNoIntentHandler())`:
```
sb.add_request_handler(RepeatIntentHandler())
```

6. Save and deploy your code. You can test this new handler by saying “repeat that” after any output. 

## Updating preset handler output
When you created your skill, a series of handlers that handle common user input or errors were built into your lambda function. You should see them below the intent handlers you’ve built so far: below **YesNoIntentHandler**, you should see **HelpIntentHandler**, followed by **CancelOrStopIntentHandler**, and so on. There are `speak_output` variables in some of these handlers that you should edit to align with what your skill is doing.

1. For example, in **HelpIntentHandler**, your skill will output "You can say hello to me! How can I help?" if the user says "help." 

To ensure the user can get help and doesn’t get confused, update this variable. Below is an example; update it according to your Amazon Kendra index’s contents.

```
speak_output = "You can ask me about AWS documentation. How can I help?"
```

2. Similarly, in **FallbackIntentHandler**, you should update the `speech` variable to suggest something useful for your skill.
3. Assign `session_attr["LastOutput"]` to the output in these handlers as well. 

## Wrapping up

There are still a lot of ways to improve your skill—it’s hard to anticipate all user responses or requests. But as you keep testing, you might find new, general examples of user input for which you can create new handlers or add utterances and slots to your intents. 

There also are other tools available in the Alexa Skills Kit you might find useful. One powerful tool is the [Persistent Attributes](https://developer.amazon.com/en-US/docs/alexa/alexa-skills-kit-sdk-for-python/manage-attributes.html#persistent-attributes) feature, which allows you to save data across sessions. You can find information on using persistent attributes in the [Cake Time tutorial](https://developer.amazon.com/en-US/alexa/alexa-skills-kit/get-deeper/tutorials-code-samples/build-an-engaging-alexa-skill). 

After you finish enhancing your skill to your liking, you can publish it so users of your product can enable the skill on their Alexa device. For more information, see [Test and Submit Your Skill for Certification](https://developer.amazon.com/en-US/docs/alexa/devconsole/test-and-submit-your-skill.html).


