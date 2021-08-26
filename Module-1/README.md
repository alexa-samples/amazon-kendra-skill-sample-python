# Module 1: Creating your skill

Now that you’ve created an Amazon Kendra index and set up your developer account, you’re ready to start building. Start by creating your skill.

1. In your Alexa Developer Console, select the **Create Skill** button on the right. 

2. In the **Skill Name** field, type a name that’s relevant to your skill, like doc support. Leave the default language as English. 

3. Choose the **Custom model** for your skill, and the **Alexa-hosted (Python)** option for backend resources. Select **Create Skill** on the top of the page.

4. On the next page select the **Start from Scratch** template, and then **Continue with Template**. This will give you a basic Python outline for your Lambda function. The skill will take a minute or so to create, and then you are ready to build!

## Setting up your skill

After your skill has been created, update what Alexa says when your skill is opened and verify that the invocation name, or the phrase that the user says to open your skill, is correct. 

1. Select the **Code** tab along the top of the console. Here you’ll find the lambda function that handles user input in the backend. 

1. Find the **LaunchRequestHandler** toward the top of the file. This is the handler that will be invoked when the skill is opened by a user, and the output will be the first thing Alexa says. 

1. Start by changing the string value of the variable `speak_output` to something that introduces the skill’s use. Below is an example.

```
speak_output = "Welcome to Doc Support. What can I help you with?"
```

You can also add a `reprompt_output` variable that the skill will say if the user doesn’t respond to the first output. See the example below for an idea; you should swap “AWS documentation” for the type of documents you added to your index. 

```
reprompt_output = "You can ask me about AWS documentation."
```

Be sure to pass your new `reprompt_output` variable to the `.ask()` method in the return line, as shown below. 

```
return (
    handler_input.response_builder
        .speak(speak_output)
        .ask(reprompt_output)
        .response
)
```

4. Quickly test the changes you’ve made so far to make sure the skill works properly. Save your code in the console, and then choose **Deploy**. 
5. Next, go to the **Build** tab to update the invocation name for your skill. Choose **Invocation** on the left sidebar to edit it.

    Type your skill name into the text box. If you’re introducing your skill in LaunchRequestHandler, use the same name for the invocation and the way you introduce your skill in the `speak_output` variable. Then press the **Save Model** and **Build Model** buttons on the top of the page.

6. When you get the notification that the full build was successful, go to the **Test** tab. In the dropdown menu at the top of the page, select **Development**. Try invoking your skill by saying or typing “Open” followed by your skill’s invocation name, e.g. “Open doc support”. Alexa should respond with the string you assigned to the `speak_output` variable. 
