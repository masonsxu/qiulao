from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.schemas import ResumeUpload, ParsedResume
from app.services.resume_parser import ResumeParserService

router = APIRouter()
parser_service = ResumeParserService()

@router.post("/parse-resume", response_model=ParsedResume)
async def parse_resume(resume_data: ResumeUpload):
    try:
        parsed_resume = parser_service.parse_markdown_resume(resume_data.markdown_content)
        return parsed_resume
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"简历解析失败: {str(e)}")

@router.post("/parse-resume-file")
async def parse_resume_file(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.md'):
            raise HTTPException(status_code=400, detail="请上传.md格式的文件")
        
        content = await file.read()
        markdown_content = content.decode('utf-8')
        
        parsed_resume = parser_service.parse_markdown_resume(markdown_content)
        return parsed_resume
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")