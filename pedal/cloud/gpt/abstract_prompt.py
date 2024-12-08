from dataclasses import dataclass
from typing import List

@dataclass
class GptFunctionPrompt:
    messages: List[dict]
    function: dict


@dataclass
class PromptMetadata:
    """
    Metadata for a prompt, to help keep track of them over time.

    Attributes:
        id: The universally unique ID of the prompt, probably generate randomly. You can put human-significant words
            too, but make sure that it won't conflict with any other prompts.
        name: The name of the prompt, which should be human-readable and concise.
        version: The version of the prompt, which should follow semvar. Git will track previous versions.
        prompt_structure_version: The version of the prompt structure that this prompt uses.
        authors: A list of authors' email of the prompt, for credit. Comma separated.
        date: The date the prompt was created, in ISO format.
        description: A human-readable description of the prompt, which can be as long as you want. Try to focus on
            why it is different from other prompts.
        based_on: The ID of the prompt that this prompt is based on, if any. If it is a new prompt, this should be
            an empty string.
    """
    id: str
    name: str
    version: str
    prompt_structure_version: str
    authors: List[str]
    date: str
    description: str
    based_on: str


class PromptStructure:
    """
    Any prompt structure, which may evolve over time. All PromptStructures should have a version number, to keep
    track of the changes over time.
    """
    version: str

    def generate(self, *args, **kwargs) -> GptFunctionPrompt:
        raise NotImplementedError("You cannot instantiate the abstract class PromptStructure. You must use a subclass.")


class PromptRegistry:
    prompts: dict[str, tuple[PromptMetadata, PromptStructure]]
    default: str

    def __init__(self):
        self.prompts = {}

    def register(self, prompt: PromptMetadata, structure: PromptStructure):
        if not self.prompts:
            self.default = prompt.id
        self.prompts[prompt.id] = (prompt, structure)

    def load(self, prompt_id: str) -> tuple[PromptMetadata, PromptStructure]:
        if not prompt_id:
            return self.prompts[self.default]
        return self.prompts[prompt_id]

    def check_prompt_exists(self, prompt_id: str) -> bool:
        return prompt_id in self.prompts

    def list_prompts(self) -> list[tuple[str, str]]:
        """
        Returns a list of all the prompts in the registry (ID, Name).
        """
        return [(key, value[0].name) for key, value in self.prompts.items()]


GLOBAL_PROMPT_REGISTRY = PromptRegistry()
