from pedal.cloud.gpt.abstract_prompt import PromptMetadata, GLOBAL_PROMPT_REGISTRY
from pedal.cloud.gpt.prompt_structures import InitialPromptStructure

GLOBAL_PROMPT_REGISTRY.register(
    PromptMetadata(id='default_prompt_1_0_0',
                   name="Default Prompt 1",
                   version="0.0.1",
                   prompt_structure_version="0.0.1",
                   authors=["acbart@udel.edu"],
                   date="2024-03-22",
                   description="The first prompt we have created.",
                   based_on=""),
    InitialPromptStructure(
        main_description="You give feedback on programming problems in Python. "
                         "The student was given the following question: {student_question}.",
        submission_description="The student answer is: {student_answer}",

        grade_function_name='give_feedback',
        grade_function_description='Give feedback on the problem.',

        score_description="An appropriate score for this question, based on the options provided.",
        is_fully_correct_description='If the student_solution is not fully correct, this parameter is'
                                     ' false.',
        reason_description='Justification for why, based on the provided rubric, question, and'
                           ' reference solution, the score is the value you gave it. This will not be shown to '
                           'the student.',
        comment_description='Helpful feedback comment to provide to the student explaining your choice '
                            'and what they should learn.',
    ))
