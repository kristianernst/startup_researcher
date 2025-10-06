from __future__ import annotations

from typing import Callable, List, Optional

try:
    from tiktoken import Encoding, get_encoding
except ImportError:  # pragma: no cover - optional dependency
    Encoding = None  # type: ignore[assignment]
    get_encoding = None  # type: ignore[assignment]
from src.models.model_register import LMModelSpec


def get_encoder(model_spec: LMModelSpec) -> Callable[[str], List[int]]:
    """
    Return a tokenizer encoder based on LMModelSpec. Prefers tokenizer_name,
    falls back to model_name. Uses tiktoken when available, otherwise
    an approximate encoder (1 token ~= 4 chars).
    """

    if model_spec.tokenizer_name == "approximate":
        return approx

    if get_encoding is None or Encoding is None:
        return approx

    if model_spec.tokenizer_name == "o200k_harmony":
        tokenizer = _get_gpt_oss_tokenizer()
        return tokenizer.encode if tokenizer else approx

    try:
        return get_encoding(model_spec.tokenizer_name).encode  # type: ignore[union-attr]
    except Exception:
        return approx


# ** GPT-OSS 20B tokenizer
_gpt_oss_20b_tokenizer: Optional[Encoding] = None


def _get_gpt_oss_tokenizer() -> Optional[Encoding]:
    global _gpt_oss_20b_tokenizer

    if _gpt_oss_20b_tokenizer is not None:
        return _gpt_oss_20b_tokenizer

    if get_encoding is None or Encoding is None:
        return None

    o200k_base = get_encoding("o200k_base")
    _gpt_oss_20b_tokenizer = Encoding(
        name="o200k_harmony",
        pat_str=o200k_base._pat_str,
        mergeable_ranks=o200k_base._mergeable_ranks,
        special_tokens={
            **o200k_base._special_tokens,
            "<|startoftext|>": 199998,
            "<|endoftext|>": 199999,
            "<|reserved_200000|>": 200000,
            "<|reserved_200001|>": 200001,
            "<|return|>": 200002,
            "<|constrain|>": 200003,
            "<|reserved_200004|>": 200004,
            "<|channel|>": 200005,
            "<|start|>": 200006,
            "<|end|>": 200007,
            "<|message|>": 200008,
            "<|reserved_200009|>": 200009,
            "<|reserved_200010|>": 200010,
            "<|reserved_200011|>": 200011,
            "<|call|>": 200012,
        }
        | {f"<|reserved_{i}|>": i for i in range(200013, 201088)},
    )
    return _gpt_oss_20b_tokenizer


# ** Fallback tokenizer (approximate)
def approx(s: str) -> List[int]:
    n = max(len(s) // 4, 1) if s else 0
    return list(range(n))


__all__ = ["get_encoder"]
