from pydantic import BaseModel, Field, field_validator

class VoiceoverLine(BaseModel):
    scene_id: int
    text: str = Field(min_length=5)
    approx_duration_sec: int

    @field_validator("approx_duration_sec", mode="before")
    @classmethod
    def normalize_duration(cls, value):
        if isinstance(value, float):
            return max(1, round(value))
        return value

class VoiceoverOutput(BaseModel):
    voiceover: list[VoiceoverLine]
