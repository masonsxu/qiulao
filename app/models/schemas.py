from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ResumeUpload(BaseModel):
    markdown_content: str
    job_hc: str

class ParsedResume(BaseModel):
    personal_info: Dict[str, Any]
    education: List[Dict[str, Any]]
    work_experience: List[Dict[str, Any]]
    skills: List[str]
    projects: List[Dict[str, Any]]
    raw_sections: Dict[str, Any]

class ExtractedKeywords(BaseModel):
    job_keywords: List[str]
    skill_keywords: List[str]
    experience_keywords: List[str]
    matched_keywords: List[str]
    missing_keywords: List[str]
    relevance_score: float

class EditSuggestion(BaseModel):
    section: str
    original_text: str
    suggested_text: str
    reason: str
    priority: str

class EditedResume(BaseModel):
    content: str
    suggestions: List[EditSuggestion]
    improvement_summary: str

class RenderedResume(BaseModel):
    html_content: str
    markdown_content: str
    pdf_url: Optional[str] = None
    created_at: datetime

class OptimizationResult(BaseModel):
    original_resume: ParsedResume
    extracted_keywords: ExtractedKeywords
    edited_resume: EditedResume
    rendered_resume: RenderedResume
    process_id: str