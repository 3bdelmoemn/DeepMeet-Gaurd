from pydantic import BaseModel,Field
from typing import Optional,List
candidate_profile = """
Name: Ahmed Youssef
Role: Backend Developer — 3 years experience
Skills: Python, FastAPI, PostgreSQL, Docker, Redis
Experience:
  - Backend Developer at TechCorp (2022–2024): Built REST APIs serving 500k users
  - Freelance Developer (2021–2022): Delivered 10+ web projects
Education: BSc Computer Science — Cairo University 2021
Projects:
  - E-commerce platform with FastAPI + PostgreSQL — reduced load time by 40%
  - Real-time chat app using WebSockets and Redis
Strengths: Fast learner, problem solver, works well under pressure
Weakness: Sometimes over-engineer solutions, actively working on shipping faster
"""
organization_info = """
Company: Paymob
Industry: Fintech — Payment Solutions
Tech Stack: Python, Microservices, Kubernetes, PostgreSQL
Role: Backend Engineer
Responsibilities:
  - Build and maintain payment processing APIs
  - Improve system reliability and performance
"""

class UserInfo(BaseModel):
    name: str = Field(..., description="The name of the candidate")
    role: str = Field(..., description="The role of the candidate")
    skills: List[str] = Field(..., description="List of skills")
    experience: List[str] = Field(..., description="List of experiences")
    education: str = Field(..., description="Education background")
    projects: List[str] = Field(..., description="List of projects")
    strengths: List[str] = Field(..., description="List of strengths")
    weaknesses: List[str] = Field(..., description="List of weaknesses")

class OrganizationInfo(BaseModel):
    company: str = Field(..., description="The name of the company")
    industry: str = Field(..., description="The industry of the company")
    tech_stack: List[str] = Field(..., description="List of technologies used")
    role: str = Field(..., description="The role being applied for")
    responsibilities: List[str] = Field(..., description="List of responsibilities for the role")