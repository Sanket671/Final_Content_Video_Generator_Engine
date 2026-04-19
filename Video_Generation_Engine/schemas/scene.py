from pydantic import BaseModel
from typing import Optional

class Scene(BaseModel):
    scene_id: int        # Add this
    scene_type: str
    duration: int
    overlay: str
    media_path: Optional[str] = "" # Add this to avoid errors
    voiceover: Optional[str] = None