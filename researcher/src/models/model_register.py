from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, ModelSettings, OpenAIResponsesModel
from agents.extensions.models.litellm_model import LitellmModel
from openai.types.shared.reasoning import Reasoning

from src.setup import settings

# Type alias for strict schema typing
TokenizerName = Literal["cl100k_base", "o200k_base", "o200k_harmony", "approximate"]


class LMModelSpec(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    model_name: str
    tokenizer_name: TokenizerName = "approximate"
    client: AsyncOpenAI | Literal["litellm"]
    max_context_length: int
    max_output_tokens: Optional[int] = None
    supports_streaming: bool
    supports_tool_calling: bool
    supports_structured_output: bool
    model_settings: ModelSettings


class ModelRegistry:
    def __init__(self):
        self.models: Dict[str, LMModelSpec] = {}

    def register_model(self, model: LMModelSpec):
        if model.model_name in self.models:
            raise ValueError(f"Model {model.model_name} already registered")
        self.models[model.model_name] = model

    def get_model(self, model_name: str) -> LMModelSpec:
        if model_name not in self.models:
            raise ValueError(
                f"Model {model_name} not registered. Available models: {self.list_models()}"
            )
        return self.models[model_name]

    def list_models(self) -> List[str]:
        return list(self.models.keys())


def get_model_from_spec(
    spec: LMModelSpec,
) -> OpenAIChatCompletionsModel | LitellmModel | OpenAIResponsesModel:
    if spec.client == "litellm":
        return LitellmModel(
            model=spec.model_name,
            base_url=settings.LLM_PROXY_BASE_URL,
            api_key="dummy",
        )

    model = OpenAIChatCompletionsModel(
        openai_client=spec.client,
        model=spec.model_name,
    )

    return model


# ** Model registry **
# *** clients to be registered.
llamacpp_client = AsyncOpenAI(base_url=settings.LLAMACPP_BASE_URL, api_key=settings.OPENAI_API_KEY)
azure_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)


model_registry = ModelRegistry()

# *** models to be registered. (TODO: perhaps we create a db for this? or a yaml?)
OSS_CAP_TOTAL_TOKENS = 0.2  # 10%
CAP_TOTAL_TOKENS = 0.1  # 10%

model_registry.register_model(
    LMModelSpec(
        model_name="gpt-oss:20b",
        client=llamacpp_client,
        max_context_length=int(131_072 * OSS_CAP_TOTAL_TOKENS),
        max_output_tokens=int(131_072 * OSS_CAP_TOTAL_TOKENS),
        tokenizer_name="o200k_harmony",
        supports_streaming=True,
        supports_tool_calling=True,
        supports_structured_output=True,
        model_settings=ModelSettings(
            temperature=0.0,
            max_tokens=20_000,
            reasoning=Reasoning(
                effort="high",
                summary=None,
            ),
        ),
    )
)

model_registry.register_model(
    LMModelSpec(
        model_name="azure.gpt-5",
        client=azure_client,
        max_context_length=int(400_000 * CAP_TOTAL_TOKENS),
        max_output_tokens=int(128_000 * CAP_TOTAL_TOKENS),
        tokenizer_name="o200k_base",
        supports_streaming=True,
        supports_tool_calling=True,
        supports_structured_output=True,
        model_settings=ModelSettings(
            parallel_tool_calls=False,
            temperature=1.0,
            # max_completion_tokens=4000, # needed for Azure gpt5
            reasoning=Reasoning(
                effort="low",
                summary="auto",
            ),
        ),
    )
)


model_registry.register_model(
    LMModelSpec(
        model_name="azure.gpt-5-nano",
        client=azure_client,
        max_context_length=int(400_000 * CAP_TOTAL_TOKENS),
        max_output_tokens=int(400_000 * CAP_TOTAL_TOKENS),
        tokenizer_name="o200k_base",
        supports_streaming=True,
        supports_tool_calling=True,
        supports_structured_output=True,
        model_settings=ModelSettings(
            parallel_tool_calls=False,
            temperature=1.0,
            # max_completion_tokens=4000, # needed for Azure gpt5
            reasoning=Reasoning(
                effort="low",
                summary="auto",
            ),
        ),
    )
)


__all__ = ["model_registry"]
