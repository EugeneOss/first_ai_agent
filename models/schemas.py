from typing import Literal
from pydantic import BaseModel, Field


class IntentClassification(BaseModel):
    input_type: Literal[
        "software_info",
        "allowed_softwares_query",
        "general_chat",
    ] = Field(description="Detected intent of the user message.")