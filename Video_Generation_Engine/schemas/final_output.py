from pydantic import BaseModel
from schemas.script import Script
from schemas.scene import Scene

class FinalOutput(BaseModel):
    product_id: str
    script: Script
    scenes: list[Scene]
    ffmpeg_command: str
