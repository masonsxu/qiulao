from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.schemas import ResumeUpload, OptimizationResult
from app.services.resume_parser import ResumeParserService
from app.services.keyword_extractor import KeywordExtractorService  
from app.services.resume_editor import ResumeEditorService
from app.services.resume_renderer import ResumeRendererService
import uuid
from datetime import datetime

router = APIRouter()

parser_service = ResumeParserService()
extractor_service = KeywordExtractorService()
editor_service = ResumeEditorService()
renderer_service = ResumeRendererService()

@router.post("/optimize-resume", response_model=OptimizationResult)
async def optimize_resume_complete(resume_data: ResumeUpload):
    """完整的简历优化流程"""
    try:
        process_id = str(uuid.uuid4())
        print(f"开始处理简历优化请求: {process_id}")
        
        # 1. 解析简历
        print("步骤1: 解析简历")
        try:
            parsed_resume = parser_service.parse_markdown_resume(resume_data.markdown_content)
            print(f"简历解析完成 - 个人信息: {len(parsed_resume.personal_info)}, 技能: {len(parsed_resume.skills)}, 工作经历: {len(parsed_resume.work_experience)}, 项目: {len(parsed_resume.projects)}, 教育: {len(parsed_resume.education)}")
            print(f"解析结果: personal_info={parsed_resume.personal_info}, skills={parsed_resume.skills[:3] if parsed_resume.skills else []}")
        except Exception as e:
            print(f"简历解析失败: {e}")
            raise HTTPException(status_code=400, detail=f"简历解析失败: {str(e)}")
        
        # 2. 提取关键字
        print("步骤2: 提取关键字")
        try:
            extracted_keywords = await extractor_service.extract_keywords(parsed_resume, resume_data.job_hc)
            print("关键字提取完成")
        except Exception as e:
            print(f"关键字提取失败: {e}")
            raise HTTPException(status_code=400, detail=f"关键字提取失败: {str(e)}")
        
        # 3. 编辑简历
        print("步骤3: 编辑简历")
        try:
            edited_resume = await editor_service.edit_resume(parsed_resume, extracted_keywords, resume_data.job_hc)
            print("简历编辑完成")
        except Exception as e:
            print(f"简历编辑失败: {e}")
            raise HTTPException(status_code=400, detail=f"简历编辑失败: {str(e)}")
        
        # 4. 渲染简历
        print("步骤4: 渲染简历")
        try:
            rendered_resume = await renderer_service.render_resume(edited_resume)
            print("简历渲染完成")
        except Exception as e:
            print(f"简历渲染失败: {e}")
            raise HTTPException(status_code=400, detail=f"简历渲染失败: {str(e)}")
        
        print(f"简历优化完成: {process_id}")
        
        return OptimizationResult(
            original_resume=parsed_resume,
            extracted_keywords=extracted_keywords,
            edited_resume=edited_resume,
            rendered_resume=rendered_resume,
            process_id=process_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"简历优化过程中发生未知错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"简历优化失败: {str(e)}")

@router.post("/optimize-resume-file")
async def optimize_resume_from_file(file: UploadFile = File(...), job_hc: str = ""):
    """从文件上传优化简历"""
    try:
        if not file.filename.endswith('.md'):
            raise HTTPException(status_code=400, detail="请上传.md格式的文件")
        
        content = await file.read()
        markdown_content = content.decode('utf-8')
        
        resume_data = ResumeUpload(
            markdown_content=markdown_content,
            job_hc=job_hc
        )
        
        return await optimize_resume_complete(resume_data)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件处理失败: {str(e)}")

@router.post("/debug-parse")
async def debug_parse_resume(resume_data: ResumeUpload):
    """调试简历解析功能"""
    try:
        print("开始调试解析")
        parsed_resume = parser_service.parse_markdown_resume(resume_data.markdown_content)
        
        return {
            "personal_info": parsed_resume.personal_info,
            "skills": parsed_resume.skills,
            "work_experience": parsed_resume.work_experience,
            "projects": parsed_resume.projects,
            "education": parsed_resume.education,
            "raw_sections": parsed_resume.raw_sections
        }
    except Exception as e:
        print(f"调试解析失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"调试解析失败: {str(e)}")

@router.post("/test-data")
async def test_data_models(resume_data: ResumeUpload):
    """测试数据模型是否正确"""
    try:
        print(f"接收到的数据: markdown_content长度={len(resume_data.markdown_content)}, job_hc长度={len(resume_data.job_hc)}")
        return {
            "status": "ok", 
            "message": "数据接收成功",
            "markdown_length": len(resume_data.markdown_content),
            "job_hc_length": len(resume_data.job_hc)
        }
    except Exception as e:
        print(f"数据验证错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"数据验证失败: {str(e)}")

@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "timestamp": datetime.now(),
        "services": {
            "parser": "active",
            "extractor": "active", 
            "editor": "active",
            "renderer": "active"
        }
    }