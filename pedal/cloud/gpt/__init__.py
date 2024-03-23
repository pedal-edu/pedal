import json
import time
import logging
from dataclasses import dataclass

from pedal.core.feedback import Feedback
from pedal.core.report import MAIN_REPORT
from pedal.cloud.constants import TOOL_NAME
from pedal.core.commands import get_submission
from pedal.cloud.gpt.abstract_prompt import GLOBAL_PROMPT_REGISTRY

try:
    import openai
except:
    openai = None

# TODO: Finish this
"gpt-api-key"

@dataclass
class Configuration:
    api_key: str
    gpt_model: str
    gpt_temperature: float
    gpt_top_p: int


class GraderApi:
    def __init__(self, config: Configuration):
        self.config = config
        if not openai:
            raise ImportError("OpenAI library not found!")
        openai.api_key = config.gpt_api_key
        if not openai.api_key:
            raise ValueError("OpenAI API key not set!")

    def run_prompt(self, messages, function, attempts=3, retry_delay=10):
        """
        Runs a prompt through OpenAI's api which calls a function, and parses the result.

        Args:
            messages: A list of messages to pass to the OpenAI api call
            function: The function to pass to the OpenAI api call
        """
        model = self.config.gpt_model
        temperature = self.config.gpt_temperature
        top_p = self.config.gpt_top_p
        if attempts <= 0:
            # TODO: Allow attempt count to be configurable
            # logger.error("Too many attempts to run prompt, aborting.")
            raise Exception("Too many attempts to run prompt, aborting.")
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                tools=[{"type": "function", "function": function}],
                tool_choice={"type": "function", "function": {
                    "name": function['name']
                }},
                #functions=[function],
                #function_call={'name': function['name']},
                temperature=temperature,
                top_p=top_p
            )
            do_retry = False
        except openai.RateLimitError as e:
            # Handle rate limit error (we recommend using exponential backoff)
            # logger.error(f"OpenAI API request exceeded rate limit: {e}")
            retry_delay *= 10
            do_retry = True
        except openai.APIConnectionError as e:
            # Handle connection error here
            # logger.error(f"Failed to connect to OpenAI API: {e}")
            raise Exception(f"Failed to connect to OpenAI API: {e}")
        except openai.APIStatusError as e:
            # Handle API error here, e.g. retry or log
            # logger.error(f"OpenAI API returned an API Error: {e.status_code}\n{e.response}\n{e.response.content}")
            do_retry = True

        if do_retry:
            # logger.error(f"Retrying prompt, waiting {retry_delay} seconds ({attempts} attempts left)")
            time.sleep(retry_delay)
            return self.run_prompt(messages, function, attempts - 1)

        if not response.choices or not response.choices[0].message.tool_calls:
            # logger.error(f"Response returned from OpenAI API was not valid: {response}")
            time.sleep(retry_delay)
            return self.run_prompt(messages, function, attempts - 1)

        # TODO: Record metadata from the response
        tool_calls = response.choices[0].message.tool_calls[0]

        try:
            args = json.loads(tool_calls.function.arguments)
        except json.JSONDecodeError as e:
            # logger.error(f"Invalid JSON returned from OpenAI API: {e}")
            time.sleep(retry_delay)
            return self.run_prompt(messages, function, attempts - 1)

        for expected_arg in function['parameters']['required']:
            if expected_arg not in args:
                # logger.error(f"Missing required parameter in OpenAI response: {expected_arg}")
                time.sleep(retry_delay)
                return self.run_prompt(messages, function, attempts - 1)

        return args, response


def run_gpt_grader(prompt: str = None, prompt_id: str = None, report=MAIN_REPORT):
    """
    Args:
        prompt (str): Either a unique prompt id or the actual prompt text.
    """
    grader = report[TOOL_NAME]['endpoints']['gpt']['api']
    metadata, prompt_skeleton = GLOBAL_PROMPT_REGISTRY.load(prompt_id)
    submission = get_submission()
    prepared_prompt = prompt_skeleton.generate(submission)
    # logger.debug(prepared_prompt)
    result, full_result = grader.run_prompt(
        messages=prepared_prompt.messages,
        function=prepared_prompt.function
    )
    # TODO: Track metadata from full_result
    return gpt_feedback(result, prepared_prompt, full_result)


class gpt_feedback(Feedback):
    def __init__(self, result, prepared_prompt, full_result, *args, **kwargs):
        self.score = result['score']
        self.correct = result['is_fully_correct']
        self.justification = result['reason']
        self.message = result['comment']
        fields = kwargs.setdefault('fields', {})
        fields['prepared_prompt'] = prepared_prompt
        fields['full_result'] = full_result
        super().__init__(*args, **kwargs)


def reset(report=MAIN_REPORT):
    """
    Resets (or initializes) the information about assertions.

    Args:
        report:
    """
    report[TOOL_NAME]['endpoints']['gpt'] = {
        'api': GraderApi()
    }