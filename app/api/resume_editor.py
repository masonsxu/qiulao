from fastapi import APIRouter, HTTPException
from app.models.schemas import ParsedResume, ExtractedKeywords, EditedResume
from app.services.resume_editor import ResumeEditorService

router = APIRouter()
editor_service = ResumeEditorService()

@router.post("/edit-resume", response_model=EditedResume)
async def edit_resume(parsed_resume: ParsedResume, extracted_keywords: ExtractedKeywords, job_hc: str):
    try:
        edited_resume = await editor_service.edit_resume(parsed_resume, extracted_keywords, job_hc)
        return edited_resume
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"简历编辑失败: {str(e)}")

@router.post("/generate-suggestions")
async def generate_edit_suggestions(parsed_resume: ParsedResume, extracted_keywords: ExtractedKeywords, job_hc: str):
    try:
        suggestions = await editor_service._generate_edit_suggestions(parsed_resume, extracted_keywords, job_hc)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"建议生成失败: {str(e)}")

@router.post("/apply-suggestions")
async def apply_suggestions(parsed_resume: ParsedResume, suggestions: list, job_hc: str):
    try:
        optimized_content = await editor_service._apply_optimizations(parsed_resume, suggestions, job_hc)
        return {"optimized_content": optimized_content}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"建议应用失败: {str(e)}")