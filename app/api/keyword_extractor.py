from fastapi import APIRouter, HTTPException
from app.models.schemas import ParsedResume, ExtractedKeywords, ResumeUpload
from app.services.keyword_extractor import KeywordExtractorService

router = APIRouter()
extractor_service = KeywordExtractorService()

@router.post("/extract-keywords", response_model=ExtractedKeywords)
async def extract_keywords(resume_data: ResumeUpload, parsed_resume: ParsedResume):
    try:
        extracted_keywords = await extractor_service.extract_keywords(parsed_resume, resume_data.job_hc)
        return extracted_keywords
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"关键字提取失败: {str(e)}")

@router.post("/analyze-match")
async def analyze_resume_job_match(resume_data: ResumeUpload, parsed_resume: ParsedResume):
    try:
        extracted_keywords = await extractor_service.extract_keywords(parsed_resume, resume_data.job_hc)
        
        analysis = {
            "relevance_score": extracted_keywords.relevance_score,
            "matched_keywords_count": len(extracted_keywords.matched_keywords),
            "missing_keywords_count": len(extracted_keywords.missing_keywords),
            "suggestions": []
        }
        
        # 生成改进建议
        if extracted_keywords.relevance_score < 0.5:
            analysis["suggestions"].append("简历与岗位匹配度较低，建议增加相关技能和经验描述")
        
        if extracted_keywords.missing_keywords:
            analysis["suggestions"].append(f"建议在简历中突出以下技能: {', '.join(extracted_keywords.missing_keywords[:5])}")
        
        return {
            "analysis": analysis,
            "extracted_keywords": extracted_keywords
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"匹配度分析失败: {str(e)}")