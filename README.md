# Project 10 build a chatbot

## Overview
This project purpose is to build and end-to-end machine learning product that help a user book a flight. It integrates Azure Cognitive Servies [LUIS](https://www.luis.ai) for Natural Language Processsing, Azure Web App for deployemnt, [Azure Application insights](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview) for performance monitoring and [Microsoft Bot Framework](https://dev.botframework.com) for developement.

## Main feature of the chatbot
* Welcome card
* Detect intention and request features in user request
* Ask for missing information
* Prompt for confirmation
* Booking card simulating flight result
* Data validation :  
      - [Text recognizer](https://github.com/microsoft/Recognizers-Text/tree/master/Python) from microsoft  
      - check for date coherency  
      - detect currency  
* Prompt multi-choice if user intent is not detected

## Frame Dataset
**Presentation** : The dialogues in Frames were collected in a Wizard-of-Oz fashion. Two humans talked to each other via a chat interface. One was playing the role of the user and the other one was playing the role of the conversational agent. We call the latter a wizard as a reference to the Wizard of Oz, the man behind the curtain. The wizards had access to a database of 250+ packages, each composed of a hotel and round-trip flights. We gave users a few constraints for each dialogue and we asked them to find the best deal. This resulted in complex dialogues where a user would often consider different options, compare packages, and progressively build the description of her ideal trip.

[Download dataset](https://www.microsoft.com/en-us/research/project/frames-dataset/)

See [Notebook](https://github.com/Falco-ops/OPCR_Booking_bot/blob/master/Notebook/proj10_data_analyse.ipynb) to clean the data and export it to the correct format to train the LUIS App.

## Import repository
```bash
git clone https://github.com/Falco-ops/OPCR_Booking_bot

```


## Install dependencies
Create virtual envrionment and instal dependencies
```console
#create env
#python3 -m venv bot_env

#install dependencies
pip install -r requirements.txt
```

## Create a LUIS Application to enable language understanding
The LUIS model for this example can be found under `CognitiveModels/FlightBooking.json` and the LUIS language model setup, training, and application configuration steps can be found [here](https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-howto-v4-luis?view=azure-bot-service-4.0&tabs=cs).

## Testing the Bot with Emulator
Bot Framework Emulator is a desktop application that allows bot developers to test and debug their bots on localhost or running remotely through a tunnel.
* Install [here](https://github.com/Microsoft/BotFramework-Emulator/releases)

To connect the bot using the bot Framework:
* Activate your environment
```console
bot_env\Scripts\activate.bat
```
* Run the bot with
```Console
python app.py
```
* Lauch Bot Framework Emulator
* file -> Open Bot
* Entre the Bot URL `http://localhost:3978/api/messages`

## Instruction for deployment
See the instruction list from Azure : [deploy your bot to Azure](https://aka.ms/azuredeployment)


## Documentation

- [Bot Framework Documentation](https://docs.botframework.com)
- [Bot Basics](https://docs.microsoft.com/azure/bot-service/bot-builder-basics?view=azure-bot-service-4.0)
- [Azure Bot Service Introduction](https://docs.microsoft.com/azure/bot-service/bot-service-overview-introduction?view=azure-bot-service-4.0)
- [Azure Bot Service Documentation](https://docs.microsoft.com/azure/bot-service/?view=azure-bot-service-4.0)
- [Azure Portal](https://portal.azure.com)
- [Language Understanding using LUIS](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/)
- [Channels and Bot Connector Service](https://docs.microsoft.com/en-us/azure/bot-service/bot-concepts?view=azure-bot-service-4.0)
- [Azure App Insight documentation](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [Deploy the bot to Azure](https://aka.ms/azuredeployment)


