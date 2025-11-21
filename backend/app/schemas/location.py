from pydantic import BaseModel

class GeocodeRequest(BaseModel):
    address: str
