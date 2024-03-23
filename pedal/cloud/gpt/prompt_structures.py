from dataclasses import dataclass

from pedal.core.submission import Submission
from pedal.cloud.gpt.abstract_prompt import PromptStructure, GptFunctionPrompt

@dataclass
class InitialPromptStructure(PromptStructure):
    """
    The structure of a prompt, which may evolve over time.
    """
    version = '0.0.1'

    main_description: str
    submission_description: str

    grade_function_name: str
    grade_function_description: str

    score_description: str
    is_fully_correct_description: str
    reason_description: str
    comment_description: str

    # gpt_get_default_prompts
    def generate(self, submission: Submission) -> GptFunctionPrompt:
        """
        Returns each prompt to run, as well as the processing function that generates feedback
        from the results. If there is an error at any point, the processing function is never called.
        """
        pieces = vars(submission)
        messages = [
            {
                'role': 'system',
                'content': self.main_description.format(**pieces)
            },
            {
                'role': 'assistant',
                'content': self.submission_description.format(**pieces)
            }
        ]
        grade_function = {
            'name': self.grade_function_name.format(**pieces),
            'description': self.grade_function_description.format(**pieces),
            'parameters': {
                'type': 'object',
                'properties': {
                    'score': {
                        'type': 'number',
                        'description': self.score_description.format(**pieces),
                    },
                    'is_fully_correct': {
                        'type': 'boolean',
                        'description': self.is_fully_correct_description.format(**pieces)
                    },
                    'reason': {
                        'type': 'string',
                        'description': self.reason_description.format(**pieces)
                    },
                    'comment': {
                        'type': 'string',
                        'description': self.comment_description.format(**pieces)
                    }
                },
                'required': ['rating_chosen', 'score', 'is_fully_correct', 'reason', 'comment']
            }
        }

        return GptFunctionPrompt(messages, grade_function)
