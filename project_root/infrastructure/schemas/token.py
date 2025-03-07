from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(..., description='Access token')
    token_type: str = Field(..., description='Token type')
