# Build an Alexa Skill that queries an Amazon Kendra index

Amazon Kendra is a powerful machine learning tool that can query a set of documents or HTML files. This tutorial shows how to integrate this service with an Alexa Skill in Python to build a seamless voice experience for document queries. Previous experience with Python and the Alexa Skills Kit is helpful, but not required, to follow this tutorial. 

## Concepts

This sample demonstrates how to use AWS resources with an Alexa-hosted Skill, including Amazon Kendra to query an index and Amazon Simple Notification Service (SNS) to send an email. 

## Prerequisites

### Amazon Kendra 
Before creating your Alexa Skill, you will need to set up an Amazon Kendra index to query from the skill. You can create an index through the Amazon Kendra console in your [AWS Management Console](https://aws.amazon.com/console/). These [instructions](https://docs.aws.amazon.com/kendra/latest/dg/create-index.html) explain how to create an index. To make your skill most effective, consider adding FAQs to your index so Alexa returns the best answers to commonly asked questions. See [Adding questions and answers directly to an index](https://docs.aws.amazon.com/kendra/latest/dg/in-creating-faq.html) for more information.

### Alexa Developer Console
You will also need an Amazon Developer account to access the Alexa Developer Console. If you don’t have an account, you can [create one](https://www.amazon.com/ap/register?clientContext=131-0331464-9465436&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&siteState=clientContext%3D142-6935021-1894360%2CsourceUrl%3Dhttps%253A%252F%252Fdeveloper.amazon.com%252Falexa%2Csignature%3Doyixlki7Yxz8bRUtt4vGJ4EugQ8j3D&marketPlaceId=ATVPDKIKX0DER&language=en_US&pageId=amzn_developer_portal&openid.return_to=https%3A%2F%2Fdeveloper.amazon.com%2Falexa&prevRID=HSRBQ1KHA4E5D1PBHPPP&openid.assoc_handle=mas_dev_portal&openid.mode=checkid_setup&prepopulatedLoginId=&failedSignInCount=0&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0). After you’ve made an account, navigate to the [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask).

## Additional Resources

If you aren’t familiar with Alexa Skills, consider starting with the [Cake Time tutorial](https://developer.amazon.com/en-US/alexa/alexa-skills-kit/get-deeper/tutorials-code-samples/build-an-engaging-alexa-skill) to learn about the different components of skill and practice building a simple skill. This tutorial will walk you through concepts like intents, slots, and handlers so you can jump into more complex concepts used in this skill. If you haven’t built a skill before, you will still be able to follow this tutorial.

## Workshop
Once you've completed the prerequisites, you can <a href="#" class="button big">[start the tutorial here](https://github.com/alexa-samples/amazon-kendra-skill-sample-python/tree/main/Module-1)</a>. Or, skip ahead to one of the modules below. 

* <a href="#" class="button big">[Module 1: Creating your Skill](https://github.com/alexa-samples/amazon-kendra-skill-sample-python/tree/main/Module-1)</a>
* <a href="#" class="button big">[Module 2: Configuring Amazon Kendra](https://github.com/alexa-samples/amazon-kendra-skill-sample-python/tree/main/Module-2)</a>
* <a href="#" class="button big">[Module 3: Finding the right response](https://github.com/alexa-samples/amazon-kendra-skill-sample-python/tree/main/Module-4)</a>
* <a href="#" class="button big">[Module 4: Doing more with your skill](https://github.com/alexa-samples/amazon-kendra-skill-sample-python/tree/main/Module-4)</a>


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
