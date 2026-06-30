from pydantic import BaseModel,Field
from typing import Optional,List

class UserInfo(BaseModel):
    name: str = Field(..., description="The name of the candidate", max_length=200)
    role: str = Field(..., description="The role of the candidate", max_length=200)
    skills: List[str] = Field(..., description="List of skills", max_length=50)
    experience: List[str] = Field(..., description="List of experiences", max_length=20)
    education: str = Field(..., description="Education background", max_length=500)
    projects: List[str] = Field(..., description="List of projects", max_length=20)
    strengths: List[str] = Field(..., description="List of strengths", max_length=20)
    weaknesses: List[str] = Field(..., description="List of weaknesses", max_length=20)

class OrganizationInfo(BaseModel):
    company: str = Field(..., description="The name of the company", max_length=200)
    industry: str = Field(..., description="The industry of the company", max_length=200)
    tech_stack: List[str] = Field(..., description="List of technologies used", max_length=50)
    role: str = Field(..., description="The role being applied for", max_length=200)
    responsibilities: List[str] = Field(..., description="List of responsibilities for the role", max_length=20)
    
class InterviewSetupRequest(BaseModel):
    user_info: UserInfo
    organization_info: OrganizationInfo