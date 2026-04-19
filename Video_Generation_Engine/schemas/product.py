from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from enum import Enum


class ProductSource(str, Enum):
    AFFILIATE = "AFFILIATE"
    DROPSHIP = "DROPSHIP"
    IN_HOUSE = "IN_HOUSE"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.upper()
            for member in cls:
                if member.value == value:
                    return member


class CinematographyProduct(BaseModel):
    id: str
    slug: str
    name: str
    brand: str
    forPet: Optional[str] = None
    petAgeGroup: Optional[str] = None
    breed: Optional[str] = ""
    category: Optional[str] = None
    athleteType: Optional[str] = None
    surface: Optional[str] = None
    description: str
    ourTake: Optional[str] = None

    metaTitle: Optional[str] = None
    metaDescription: Optional[str] = None

    tags: List[str] = Field(default_factory=list)

    originalPrice: float
    finalPrice: float
    discountPercentage: int

    rating: float
    reviews: int

    user_reviews: List[str] = Field(default_factory=list)

    images: List[HttpUrl]
    videoUrl: Optional[HttpUrl] = None

    source: ProductSource
    affiliateLink: Optional[str] = None
    externalId: Optional[str] = None

    sellerName: str
    inStock: bool = False
    appCategory: str
