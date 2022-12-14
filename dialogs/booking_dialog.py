# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datatypes_date_time.timex import Timex
import recognizers_suite as Recognizers
from recognizers_suite import Culture, ModelResult
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions, NumberPrompt, PromptValidatorContext
from botbuilder.core import MessageFactory
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog
from .departure_date_resolver_dialog import DepartureDateResolverDialog
from .return_date_resolver_dialog import ReturnDateResolverDialog


class BookingDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(BookingDialog, self).__init__(dialog_id or BookingDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(DepartureDateResolverDialog(DepartureDateResolverDialog.__name__))
        self.add_dialog(ReturnDateResolverDialog(ReturnDateResolverDialog.__name__))
        self.add_dialog(TextPrompt("budget", BookingDialog.budget_validator))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.origin_step,
                    self.destination_step,
                    self.departure_date_step,
                    self.return_date_step,
                    self.budget_step,
                    self.confirm_step,
                    self.final_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    async def origin_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If an origin city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        if booking_details.origin is None:
            message_text = "From which city will you be leaving?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.origin)

    async def destination_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If a destination city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.origin = step_context.result.capitalize()
        if booking_details.destination is None:
            message_text = "What will your destination be for your vacation?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.destination)

    async def departure_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a departure date has not been provided, prompt for one.
        This will use the DEPARTURE_DATE_RESOLVER_DIALOG.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.destination = step_context.result.capitalize()
        if not booking_details.departure_date or self.is_ambiguous(
            booking_details.departure_date
        ):
            return await step_context.begin_dialog(
                DepartureDateResolverDialog.__name__, booking_details.departure_date
            )
        return await step_context.next(booking_details.departure_date)
    
    async def return_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a return date has not been provided, prompt for one.
        This will use the RETURN_DATE_RESOLVER_DIALOG.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options
        

        # Capture the results of the previous step
        booking_details.departure_date = step_context.result
        if not booking_details.return_date or self.is_ambiguous(
            booking_details.return_date
        ):
            return await step_context.begin_dialog(
                ReturnDateResolverDialog.__name__, booking_details #### 
            )
        return await step_context.next(booking_details.return_date)

    async def budget_step(self, step_context: WaterfallStepContext
                        ) -> DialogTurnResult:
        """
        If a budget has not been provided, prompt for one. Pormpt validator to check for 
        prositive integer. The check is only done during waterfall dialog. 
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options
        # Capture the response to the previous step's prompt
        booking_details.return_date = step_context.result

        if booking_details.budget is None:
            message_text = "And what is your budget for this trip ?"
            repromt_text = 'Sorry I didn\'t get that. Try giving me a number. If you don\'t mention it, the currency will be in euros.'
            prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
            reprompt_message = MessageFactory.text(repromt_text)
            return await step_context.prompt(
                "budget", 
                PromptOptions(
                    prompt=prompt_message,
                    retry_prompt=reprompt_message))
                
        return await step_context.next(booking_details.budget)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        Confirm the information the user has provided.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the results of the previous step budget and currency
        currency = Recognizers.recognize_currency(step_context.result, Culture.English)
        budget = Recognizers.recognize_number(step_context.result, Culture.English)
        booking_details.budget = budget[0].resolution['value']
        if len(currency)>0:
            booking_details.currency = currency[0].resolution["unit"]
        message_text = (
            f"Could you please confirm, I have you traveling to: { booking_details.destination } from: "
            f"{ booking_details.origin }. You will be leaving on the: { booking_details.departure_date} "
            f"and returning on the: {booking_details.return_date}. "
            f"And your budget is {booking_details.budget} {booking_details.currency}"
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Complete the interaction and end the dialog.
        :param step_context:
        :return DialogTurnResult:
        """
        #is a yes or no
        booking_details = step_context.options

        # We want to save the data saved by the bot to send to telemetry.
        #properties = {}
        #properties["origin"] = booking_details.origin
        #properties["destination"] = booking_details.destination
        #properties["departure_date"] = booking_details.departure_date
        #properties["return_date"] = booking_details.return_date
        #properties["budget"] = booking_details.budget

        #if the bot was succeful
        if step_context.result:
            #location for app insight trace track
            #self.telemetry_client.track_trace("Bot successful", properties, "INFO")
            print('Send telemetry trace BOT SUCESSFUL')
            return await step_context.end_dialog(booking_details)

        else:
            #bot apologizes (promt for feedback dialog?)
            message_text = "I am sorry I couldn't help you"
            prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
            )

            await step_context.context.send_activity(prompt_message)
            print('Send telemetry trace BOT UNSUCESSFUL')
            #track trace to telemetry
            #self.telemetry_client.track_trace("Bot unsuccessful", properties, "ERROR")

        #end dialog    
        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        timex_property = Timex(timex)
        return "definite" not in timex_property.types

    @staticmethod
    async def budget_validator(prompt_context: PromptValidatorContext) -> bool:
        # This condition is our validation rule. positive number
        budget = Recognizers.recognize_number(prompt_context.recognized.value, Culture.English)
        #if no number are recognize it will return an empty list
        if len(budget)>0:
            return True
        return False

