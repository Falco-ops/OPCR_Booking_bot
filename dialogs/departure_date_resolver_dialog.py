# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datatypes_date_time.timex import Timex
import datetime
from datetime import date

from botbuilder.core import MessageFactory
from botbuilder.dialogs import WaterfallDialog, DialogTurnResult, WaterfallStepContext
from botbuilder.dialogs.prompts import (
    DateTimePrompt,
    PromptValidatorContext,
    PromptOptions,
    DateTimeResolution,
)
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog


class DepartureDateResolverDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(DepartureDateResolverDialog, self).__init__(
            dialog_id or DepartureDateResolverDialog.__name__
        )

        self.add_dialog(
            DateTimePrompt(
                "Departure", DepartureDateResolverDialog.departure_prompt_validator
            )
        )
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__ + "2", [self.initial_step, self.final_step]
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__ + "2"

    async def initial_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        timex = step_context.options

        prompt_msg_text = "On what date would you like to travel?"
        prompt_msg = MessageFactory.text(
            prompt_msg_text, prompt_msg_text, InputHints.expecting_input
        )

        reprompt_msg_text = "I'm sorry, for best results, please enter your travel date including the month, " \
                            "day and year. Make sure your date is not anterior of today"
        reprompt_msg = MessageFactory.text(
            reprompt_msg_text, reprompt_msg_text, InputHints.expecting_input
        )

        if timex is None:
            # We were not given any date at all so prompt the user.
            return await step_context.prompt(
                "Departure",
                PromptOptions(prompt=prompt_msg, 
                    retry_prompt=reprompt_msg,
                    number_of_attempts = 1),
            )
        # We have a Date we just need to check it is unambiguous.
        if "definite" not in Timex(timex).types:
            # This is essentially a "reprompt" of the data we were given up front.
            return await step_context.prompt(
                DateTimePrompt.__name__, PromptOptions(prompt=reprompt_msg)
            )

        return await step_context.next(DateTimeResolution(timex=timex))

    async def final_step(self, step_context: WaterfallStepContext):
        timex = step_context.result[0].timex
        return await step_context.end_dialog(timex)

    @staticmethod
    async def departure_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        
        #we check that we have all information for the date day month and year
        if prompt_context.recognized.succeeded:
            if len(prompt_context.recognized.value[0].timex.split('-')) == 3:
            
                timex = prompt_context.recognized.value[0].timex#.split("T")[0]
                dep_date = datetime.datetime(int(timex.split("-")[0]), int(timex.split("-")[1]), 
                    int(timex.split("-")[2])
                )
                today = datetime.datetime(date.today().year, date.today().month, date.today().day)
                #compare if date given is coherent i.e. after the current day
                if dep_date >= today:
                # TODO: Needs TimexProperty
                    return "definite" in Timex(timex).types
                else:
                    if prompt_context.options.number_of_attempts > 1:
                    #track trace to telemetry
                    #self.telemetry_client.track_trace("LOOP departure date", "ERROR")
                        print(f"number of attemps is {prompt_context.options.number_of_attempts}, send telemetry STUCK IN LOOP")    
            else:
               if prompt_context.options.number_of_attempts > 1:
                #track trace to telemetry
                #self.telemetry_client.track_trace("LOOP departure date", "ERROR")
                    print(f"number of attemps is {prompt_context.options.number_of_attempts}, send telemetry STUCK IN LOOP") 
        else:
            if prompt_context.options.number_of_attempts > 1:
            #track trace to telemetry
            #self.telemetry_client.track_trace("LOOP departure date", "ERROR")
                print(f"number of attemps is {prompt_context.options.number_of_attempts}, send telemetry STUCK IN LOOP")


        return False
