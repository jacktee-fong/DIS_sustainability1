from pydantic import BaseModel, Field
from typing import Optional, Sequence


class BuildingDataResponse(BaseModel):
    code: str = Field(title="Building Asset Code")
    name: str = Field(title="Building Asset Name")
    address: str = Field(title="Address")
    country: str = Field(title="Country", default="Singapore")
    active: bool = Field(title="Active", default=True)
    city: str = Field(title="City", default="Singapore")
    box: Sequence[list] = Field(title="Building map's box")
    net_area: float = Field(title="Net Area", description="Floor Area listed on website")
    floor: str = Field(title="Typical Floor Area", description="Typical Floor Area")
    MRT: str = Field(title="MRT", description="Nearest MRT station")
    carpark: str = Field(title="Carpark", description="Available parking space")
    award: str = Field(title="award", description="Award winning")
    average_visitor: Optional[float] = Field(title="average_visitor", description="Average visitor", default=0)
    total_staff: Optional[int] = Field(title="total_staff", description="Total staff", default=0)
    working_day: Optional[int] = Field(title="working_day", description="Working day", default=22)
    description: Optional[str] = Field(title="description", description="Description of the building")
    photo: Optional[str] = Field(title="photo", description="base64 image")