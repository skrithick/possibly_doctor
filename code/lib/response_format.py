from pydantic import BaseModel, Field


class Response(BaseModel):
    urgency_level: int = Field(
        description='1 = General Info/Theory. 2 = Manageable Symptoms/Home Care. 3 = Life-threatening Emergency.'
    )

    response: str = Field(
        description='The grounded medical advice based ONLY on context.'
    )

    confidence: float = Field(
        description='The confidence of the model in its response, based on the relevance of the context.'
    )

class CheckerResponse(BaseModel):
    danger: bool = Field(
        description='Indicates if the query is dangerous.'
    )

    reason: str = Field(
        description='The reason why the query is considered dangerous, if applicable.'
    )

class SummaryResponse(BaseModel):
    summary: str = Field(
        description='A concise summary of the recent messages.'
    )