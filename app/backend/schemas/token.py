from pydantic import BaseModel


class RefreshTokenRequest(BaseModel):
    refresh_token: str

class EventTokensResponse(BaseModel):
    refresh_token: str | None
    access_toke: str | None
    token_type: str