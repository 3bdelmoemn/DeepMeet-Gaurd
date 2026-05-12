from server.utilities import convert_to_wav
from server.usecases import InterViewAssistant
from server.models.schemas import UserInfo,OrganizationInfo

ref_text_path=r"D:\Education\GraduationProject\last version\DeepMeet-Gaurd\src\assets\refrences\my text.txt"
ref_audio_path=r"D:\Education\GraduationProject\last version\DeepMeet-Gaurd\src\assets\refrences\my real voice.wav"


user_info={
    "name":"Abdullah Mohamed Ahmed Saied",
    "role":"AI Engineer",
    "skills":["Python","Machine Learning","Deep Learning","NLP","Computer Vision"],
    "experience":[
        "AI Engineer at Tech Innovators (2022–Present): Developed ML models for predictive analytics",
        "Data Scientist at Data Solutions (2020–2022): Built data pipelines and performed analysis for clients"
    ],
    "education":"Bachelor of Science in Computer Science",
    "projects":[
        "Developed a chatbot using NLP techniques",
        "Built a recommendation system for an e-commerce platform"
    ],
    "strengths":[
        "Strong problem-solving skills",
        "Excellent communication abilities"
    ],
    "weaknesses":[
        "Sometimes overthink solutions",
        "Can be a perfectionist"
    ]
}

organization_info={
    "company":"amazon",
    "industry":"E-commerce and Cloud Computing",
    "tech_stack":["Python","AWS","Microservices","Docker"],
    "role":"AI Engineer",
    "responsibilities":[
        "Design and implement AI solutions to improve customer experience",
        "Collaborate with cross-functional teams to deploy machine learning models"
    ]
}

if __name__ == "__main__":
    assistant=InterViewAssistant()
    assistant.setup(ref_audio_path=ref_audio_path,ref_text_content=ref_text_path)
    assistant.impersonate(user_info=UserInfo(**user_info),organization_info=OrganizationInfo(**organization_info))
    assistant.communicate()