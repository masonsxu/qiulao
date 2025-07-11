import openai
import re
import jieba
from typing import List, Set
from app.models.schemas import ParsedResume, ExtractedKeywords
from app.core.config import settings

class KeywordExtractorService:
    def __init__(self):
        if settings.enable_ai and settings.openai_api_key:
            self.client = openai.OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )
        else:
            self.client = None
            print("AI功能已禁用，将使用基础算法进行关键字提取")
        
        self.tech_keywords = {
            'programming_languages': ['Python', 'Java', 'JavaScript', 'C++', 'Go', 'Rust', 'TypeScript'],
            'frameworks': ['Django', 'Flask', 'FastAPI', 'Spring', 'React', 'Vue', 'Angular'],
            'databases': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle'],
            'tools': ['Docker', 'Kubernetes', 'Git', 'Jenkins', 'AWS', 'Azure']
        }
    
    async def extract_keywords(self, parsed_resume: ParsedResume, job_hc: str) -> ExtractedKeywords:
        job_keywords = await self._extract_job_keywords(job_hc)
        
        resume_text = self._resume_to_text(parsed_resume)
        resume_keywords = self._extract_resume_keywords(resume_text)
        
        skill_keywords = self._extract_skill_keywords(parsed_resume.skills)
        experience_keywords = self._extract_experience_keywords(parsed_resume.work_experience)
        
        matched_keywords = list(set(job_keywords) & set(resume_keywords))
        missing_keywords = list(set(job_keywords) - set(resume_keywords))
        
        relevance_score = len(matched_keywords) / len(job_keywords) if job_keywords else 0
        
        return ExtractedKeywords(
            job_keywords=job_keywords,
            skill_keywords=skill_keywords,
            experience_keywords=experience_keywords,
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            relevance_score=relevance_score
        )
    
    async def _extract_job_keywords(self, job_hc: str) -> List[str]:
        prompt = f"""
        请从以下岗位描述中提取关键技能和要求关键字：

        {job_hc}

        请提取：
        1. 技术技能关键字
        2. 工作经验相关关键字
        3. 行业相关关键字
        4. 软技能关键字

        请以JSON格式返回，格式如下：
        {{"keywords": ["关键字1", "关键字2", ...]}}
        """
        
        try:
            response = await self._call_openai(prompt)
            if response:  # 如果API调用成功
                keywords_data = self._parse_json_response(response)
                if keywords_data.get("keywords"):
                    return keywords_data["keywords"]
            # 如果API调用失败或没有返回有效数据，使用fallback
            return self._extract_keywords_fallback(job_hc)
        except Exception as e:
            print(f"关键字提取失败，使用备用方案: {e}")
            return self._extract_keywords_fallback(job_hc)
    
    async def _call_openai(self, prompt: str) -> str:
        if not self.client:
            return ""  # 如果没有AI客户端，直接返回空字符串
        
        try:
            response = self.client.chat.completions.create(
                model=settings.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            # 返回空字符串，触发fallback逻辑
            return ""
    
    def _parse_json_response(self, response: str) -> dict:
        import json
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        return {}
    
    def _extract_keywords_fallback(self, job_hc: str) -> List[str]:
        keywords = []
        
        # 提取技术关键字
        for category, tech_list in self.tech_keywords.items():
            for tech in tech_list:
                if tech.lower() in job_hc.lower():
                    keywords.append(tech)
        
        # 使用jieba分词提取中文关键字
        words = jieba.lcut(job_hc)
        filtered_words = [word for word in words if len(word) >= 2 and word.isalnum()]
        keywords.extend(filtered_words[:20])  # 取前20个词
        
        return list(set(keywords))
    
    def _resume_to_text(self, parsed_resume: ParsedResume) -> str:
        text_parts = []
        
        # 添加技能
        if parsed_resume.skills:
            text_parts.extend(parsed_resume.skills)
        
        # 添加工作经验
        for work in parsed_resume.work_experience:
            text_parts.append(work.get('company', ''))
            text_parts.append(work.get('position', ''))
            if 'responsibilities' in work:
                text_parts.extend(work['responsibilities'])
        
        # 添加项目经验
        for project in parsed_resume.projects:
            text_parts.append(project.get('name', ''))
            text_parts.append(project.get('technologies', ''))
            if 'description' in project:
                if isinstance(project['description'], list):
                    text_parts.extend(project['description'])
                else:
                    text_parts.append(project['description'])
        
        return ' '.join(text_parts)
    
    def _extract_resume_keywords(self, resume_text: str) -> List[str]:
        keywords = []
        
        # 提取技术关键字
        for category, tech_list in self.tech_keywords.items():
            for tech in tech_list:
                if tech.lower() in resume_text.lower():
                    keywords.append(tech)
        
        # 使用jieba分词
        words = jieba.lcut(resume_text)
        filtered_words = [word for word in words if len(word) >= 2 and word.isalnum()]
        keywords.extend(filtered_words)
        
        return list(set(keywords))
    
    def _extract_skill_keywords(self, skills: List[str]) -> List[str]:
        skill_keywords = []
        for skill in skills:
            # 分割技能字符串
            parts = re.split(r'[,，、\s]+', skill)
            skill_keywords.extend([part.strip() for part in parts if part.strip()])
        
        return list(set(skill_keywords))
    
    def _extract_experience_keywords(self, work_experience: List[dict]) -> List[str]:
        experience_keywords = []
        
        for work in work_experience:
            # 提取公司相关关键字
            company = work.get('company', '')
            if company:
                experience_keywords.append(company)
            
            # 提取职位相关关键字
            position = work.get('position', '')
            if position:
                experience_keywords.append(position)
            
            # 提取工作职责关键字
            responsibilities = work.get('responsibilities', [])
            for resp in responsibilities:
                words = jieba.lcut(resp)
                filtered_words = [word for word in words if len(word) >= 2]
                experience_keywords.extend(filtered_words)
        
        return list(set(experience_keywords))