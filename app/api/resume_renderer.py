from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from app.models.schemas import EditedResume, RenderedResume
from app.services.resume_renderer import ResumeRendererService

router = APIRouter()
renderer_service = ResumeRendererService()

@router.post("/render-resume", response_model=RenderedResume)
async def render_resume(edited_resume: EditedResume):
    try:
        rendered_resume = await renderer_service.render_resume(edited_resume)
        return rendered_resume
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"简历渲染失败: {str(e)}")

@router.post("/render-with-template", response_model=RenderedResume)
async def render_with_template(
    edited_resume: EditedResume, 
    template: str = Query(default="modern", description="模板类型: modern, professional, creative, technical")
):
    try:
        rendered_resume = await renderer_service.render_with_template(edited_resume, template)
        return rendered_resume
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"模板渲染失败: {str(e)}")

@router.post("/preview-html", response_class=HTMLResponse)
async def preview_html(edited_resume: EditedResume):
    try:
        rendered_resume = await renderer_service.render_resume(edited_resume)
        return HTMLResponse(content=rendered_resume.html_content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"HTML预览失败: {str(e)}")

@router.get("/templates")
async def get_available_templates():
    return {
        "templates": [
            {"name": "modern", "description": "现代简洁风格"},
            {"name": "professional", "description": "商务专业风格"},
            {"name": "creative", "description": "创意设计风格"},
            {"name": "technical", "description": "技术专业风格"}
        ]
    }