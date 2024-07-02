from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from dbally.audit.events import LLMEvent
from dbally.llms.clients.base import LLMClient, LLMOptions

from ..._types import NOT_GIVEN, NotGiven


@dataclass
class LocalLLMOptions(LLMOptions):
    """
    Dataclass that represents all available LLM call options for the local LLM client.
    Each of them is described in the [HuggingFace documentation]
    (https://huggingface.co/docs/huggingface_hub/en/package_reference/inference_client#huggingface_hub.InferenceClient.text_generation). # pylint: disable=line-too-long
    """

    repetition_penalty: Union[Optional[float], NotGiven] = NOT_GIVEN
    do_sample: Union[Optional[bool], NotGiven] = NOT_GIVEN
    best_of: Union[Optional[int], NotGiven] = NOT_GIVEN
    max_new_tokens: Union[Optional[int], NotGiven] = NOT_GIVEN
    top_k: Union[Optional[int], NotGiven] = NOT_GIVEN
    top_p: Union[Optional[float], NotGiven] = NOT_GIVEN
    seed: Union[Optional[int], NotGiven] = NOT_GIVEN
    stop_sequences: Union[Optional[List[str]], NotGiven] = NOT_GIVEN
    temperature: Union[Optional[float], NotGiven] = NOT_GIVEN


class LocalLLMClient(LLMClient[LocalLLMOptions]):
    """
    Client for the local LLM that supports Hugging Face models.
    """

    _options_cls = LocalLLMOptions

    def __init__(
        self,
        model_name: str,
        *,
        hf_api_key: Optional[str] = None,
    ) -> None:
        """
        Constructs a new local LLMClient instance.

        Args:
            model_name: Name of the model to use.
            hf_api_key: The Hugging Face API key for authentication.
        """

        super().__init__(model_name)

        self.tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_api_key)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, device_map="auto", torch_dtype=torch.bfloat16, token=hf_api_key
        )

    async def call(
        self,
        prompt: torch.tensor,
        response_format: Optional[Dict[str, str]],
        options: LocalLLMOptions,
        event: LLMEvent,
    ) -> str:
        """
        Makes a call to the local LLM with the provided prompt and options.

        Args:
            prompt: Tokenized prompt.
            response_format: Optional argument used in the OpenAI API - used to force the json output.
            options: Additional settings used by the LLM.
            event: Container with the prompt, LLM response, and call metrics.

        Returns:
            Response string from LLM.
        """

        outputs = self.model.generate(
            prompt,
            eos_token_id=self.tokenizer.eos_token_id,
            **options.dict(),
        )

        response = outputs[0][prompt.shape[-1] :]

        event.completion_tokens = len(outputs[0][prompt.shape[-1] :])
        event.prompt_tokens = len(outputs[0][: prompt.shape[-1]])
        event.total_tokens = prompt.shape[-1]

        decoded_response = self.tokenizer.decode(response, skip_special_tokens=True)

        return decoded_response
