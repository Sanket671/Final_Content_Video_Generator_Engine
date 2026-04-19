from pydantic import BaseModel

class VideoScript(BaseModel):
    hook_vo: str  # For the Pexels video
    problem_vo: str # The "Why it matters" part
    product_intro_vo: str # Introducing the brand name
    social_proof_vo: str # "Customers noticed..." (using reviews)
    features_vo: list[str] # Point-wise benefits for the blue background scenes
    outro_vo: str # Sponsored by Reticulo
