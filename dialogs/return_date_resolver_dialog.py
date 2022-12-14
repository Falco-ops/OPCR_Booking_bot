# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datatypes_date_time.timex import Timex

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


class ReturnDateResolverDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(ReturnDateResolverDialog, self).__init__(
            dialog_id or ReturnDateResolverDialog.__name__
        )

        self.add_dialog(
            DateTimePrompt(
                DateTimePrompt.__name__, ReturnDateResolverDialog.datetime_prompt_validator
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
        booking_details = step_context.options
        timex = booking_details.return_date
        dep_date = booking_details.departure_date
        

        prompt_msg_text = "On what date would you like to travel back?"
        prompt_msg = MessageFactory.text(
            prompt_msg_text, prompt_msg_text, InputHints.expecting_input
        )

        reprompt_msg_text = ("I'm sorry, something is wrong with your date. Check the following :\n is your format correct (DD-MM-YYYY is best).\n Verify that your return date is after your departure date.")

        
        reprompt_msg = MessageFactory.text(
            reprompt_msg_text, reprompt_msg_text, InputHints.expecting_input
        )

        if timex is None:
            # We were not given any date at all so prompt the user. we pass the departure date as options
            #for the prompt validator
            #set number of attempts to 0
            return await step_context.prompt(
                DateTimePrompt.__name__,
                PromptOptions(prompt=prompt_msg,
                retry_prompt=reprompt_msg,
                number_of_attempts=1,
                validations=dep_date)
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
    async def datetime_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        
        if prompt_context.recognized.succeeded:
            timex = prompt_context.recognized.value[0].timex.split("T")[0]
            return_date = prompt_context.recognized.value[0].timex
            dep_date = prompt_context.options.validations
            if dep_date < return_date:
              
                # TODO: Needs TimexProperty
                return "definite" in Timex(timex).types
            else:
                if prompt_context.options.number_of_attempts > 1:
                #track trace to telemetry
                #self.telemetry_client.track_trace("LOOP return date", "ERROR")
                    print(f"number of attemps is {prompt_context.options.number_of_attempts}, send telemetry STUCK IN LOOP")
        
        else:
            if prompt_context.options.number_of_attempts > 1:
            #track trace to telemetry
            #self.telemetry_client.track_trace("LOOP return date", "ERROR")
                print(f"number of attemps is {prompt_context.options.number_of_attempts}, send telemetry STUCK IN LOOP")

        return False
