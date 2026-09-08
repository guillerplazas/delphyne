"""Budgeted embedding calls for ACE, with the ordinary cache unchanged.

text-embedding-3-small: $0.02/M input tokens, checked 2026-09-08 against
https://developers.openai.com/api/docs/models/text-embedding-3-small .
"""

# pyright: strict

import os
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import override

import numpy as np
import openai
import tiktoken

from campaign_budget import Ledger
from delphyne.stdlib.embeddings import (
    EmbeddingModel,
    EmbeddingResponse,
    OpenAICompatibleEmbeddingModel,
    standard_openai_embedding_model,
)


@dataclass
class CampaignEmbeddingModel(OpenAICompatibleEmbeddingModel):
    @override
    def _embed(self, batch: Sequence[str]) -> Sequence[EmbeddingResponse]:
        assert self.dollars_per_token is not None
        ledger = Ledger(Path(os.environ["OMPHALOS_CAMPAIGN_LEDGER"]))
        rate = self.dollars_per_token
        key = ledger.reserve(
            os.environ["OMPHALOS_CAMPAIGN_STAGE"],
            self.model_name,
            (sum(len(s.encode()) for s in batch) + 1024) * rate,
            os.environ.get("OMPHALOS_CAMPAIGN_CELL", "embeddings"),
        )
        try:
            with openai.OpenAI(max_retries=0, timeout=600) as client:
                response = client.embeddings.create(
                    model=self.model_name, input=list(batch)
                )
        except Exception as ex:
            rejected = isinstance(
                ex, openai.APIStatusError
            ) and ex.status_code in {
                400,
                401,
                403,
                404,
                422,
                429,
            }
            ledger.settle(
                key,
                0.0 if rejected else None,
                {"exception": type(ex).__name__},
            )
            raise
        ledger.settle(
            key, response.usage.total_tokens * rate, response.usage.to_dict()
        )
        vectors = {d.index: d.embedding for d in response.data}
        encoder = tiktoken.get_encoding("cl100k_base")
        return [
            EmbeddingResponse(
                model=response.model,
                embedding=np.array(vectors[i], dtype=np.float32),
                total_tokens=len(encoder.encode(s)),
            )
            for i, s in enumerate(batch)
        ]


def embedding_model(name: str) -> EmbeddingModel:
    model = standard_openai_embedding_model(name)
    if not os.environ.get("OMPHALOS_CAMPAIGN_LEDGER"):
        return model
    if name != "text-embedding-3-small":
        raise ValueError("campaign has no price for this embedding model")
    return CampaignEmbeddingModel(model_name=name, dollars_per_token=0.02e-6)
