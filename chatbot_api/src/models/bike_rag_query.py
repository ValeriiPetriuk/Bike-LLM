from pydantic import BaseModel

class BikeQueryInput(BaseModel):
    text: str

class BikeQueryOutput(BaseModel):
    input: str
    output: str
    intermediate_steps: list[str]