import openai
import re
from typing import List, Dict, Any
from app.models.schemas import ParsedResume, ExtractedKeywords, EditedResume, EditSuggestion
from app.core.config import settings

class ResumeEditorService:
    def __init__(self):
        if settings.enable_ai and settings.openai_api_key:
            self.client = openai.OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )
        else:
            self.client = None
            print("AI功能已禁用，将使用基础算法进行简历编辑")
    
    async def edit_resume(self, parsed_resume: ParsedResume, extracted_keywords: ExtractedKeywords, job_hc: str) -> EditedResume:
        suggestions = await self._generate_edit_suggestions(parsed_resume, extracted_keywords, job_hc)
        
        optimized_content = await self._apply_optimizations(parsed_resume, suggestions, job_hc)
        
        improvement_summary = await self._generate_improvement_summary(suggestions)
        
        return EditedResume(
            content=optimized_content,
            suggestions=suggestions,
            improvement_summary=improvement_summary
        )
    
    async def _generate_edit_suggestions(self, parsed_resume: ParsedResume, extracted_keywords: ExtractedKeywords, job_hc: str) -> List[EditSuggestion]:
        suggestions = []
        
        # 技能部分建议
        skills_suggestions = await self._suggest_skills_improvements(parsed_resume.skills, extracted_keywords, job_hc)
        suggestions.extend(skills_suggestions)
        
        # 工作经验建议
        work_suggestions = await self._suggest_work_experience_improvements(parsed_resume.work_experience, extracted_keywords, job_hc)
        suggestions.extend(work_suggestions)
        
        # 项目经验建议
        project_suggestions = await self._suggest_project_improvements(parsed_resume.projects, extracted_keywords, job_hc)
        suggestions.extend(project_suggestions)
        
        return suggestions
    
    async def _suggest_skills_improvements(self, skills: List[str], extracted_keywords: ExtractedKeywords, job_hc: str) -> List[EditSuggestion]:
        suggestions = []
        
        current_skills_text = "\n".join(skills) if skills else "无技能描述"
        
        prompt = f"""
        当前技能描述：
        {current_skills_text}
        
        岗位要求：
        {job_hc}
        
        缺失的关键技能：
        {', '.join(extracted_keywords.missing_keywords[:10])}
        
        请为技能部分提供优化建议，要求：
        1. 突出与岗位相关的技能
        2. 整合缺失的关键技能
        3. 使用更专业的表达方式
        4. 保持真实性，不添加虚假技能
        
        请以JSON格式返回建议：
        {{"suggestions": [{{"original": "原文", "improved": "改进后", "reason": "改进原因"}}]}}
        """
        
        try:
            response = await self._call_openai(prompt)
            if response:  # 如果API调用成功
                suggestions_data = self._parse_json_response(response)
                
                for suggestion in suggestions_data.get("suggestions", []):
                    suggestions.append(EditSuggestion(
                        section="技能",
                        original_text=suggestion.get("original", ""),
                        suggested_text=suggestion.get("improved", ""),
                        reason=suggestion.get("reason", ""),
                        priority="high"
                    ))
            else:
                # API调用失败时的备用建议
                if extracted_keywords.missing_keywords:
                    suggestions.append(EditSuggestion(
                        section="技能",
                        original_text=current_skills_text,
                        suggested_text=current_skills_text + "\n- " + "\n- ".join(extracted_keywords.missing_keywords[:5]),
                        reason="建议添加岗位要求的关键技能",
                        priority="high"
                    ))
        except Exception as e:
            print(f"技能建议生成失败: {e}")
            # 提供基础的改进建议
            if extracted_keywords.missing_keywords:
                suggestions.append(EditSuggestion(
                    section="技能",
                    original_text=current_skills_text,
                    suggested_text=current_skills_text + "\n- " + "\n- ".join(extracted_keywords.missing_keywords[:5]),
                    reason="建议添加岗位要求的关键技能",
                    priority="high"
                ))
        
        return suggestions
    
    async def _suggest_work_experience_improvements(self, work_experience: List[Dict[str, Any]], extracted_keywords: ExtractedKeywords, job_hc: str) -> List[EditSuggestion]:
        suggestions = []
        
        for i, work in enumerate(work_experience):
            work_text = work.get('raw_text', '')
            if not work_text:
                continue
            
            # 只做基础的格式和表达优化，不添加虚构内容
            prompt = f"""
            当前工作经历描述：
            {work_text}
            
            岗位要求：
            {job_hc}
            
            请对这段工作经历进行表达优化，要求：
            1. 保持所有事实内容不变，不添加任何虚构信息
            2. 优化语言表达，使其更专业和简洁
            3. 调整句式结构，突出重点成就
            4. 如果内容中提到的技术与岗位要求匹配，可以适当强调
            5. 绝对不能编造数据、项目名称、技术栈或工作成果
            
            请以JSON格式返回：
            {{"improved_text": "优化后的文本", "reason": "优化原因"}}
            """
            
            try:
                response = await self._call_openai(prompt)
                if response:  # 如果API调用成功
                    suggestion_data = self._parse_json_response(response)
                    
                    if suggestion_data.get("improved_text"):
                        # 验证优化内容是否过于偏离原文
                        original_length = len(work_text)
                        improved_length = len(suggestion_data["improved_text"])
                        
                        # 如果优化后的内容长度增加超过50%，可能包含虚构内容，使用原文
                        if improved_length > original_length * 1.5:
                            continue
                        
                        suggestions.append(EditSuggestion(
                            section=f"工作经历{i+1}",
                            original_text=work_text,
                            suggested_text=suggestion_data["improved_text"],
                            reason=suggestion_data.get("reason", "优化工作描述表达"),
                            priority="medium"
                        ))
                else:
                    # API调用失败时，只做基础的关键词优化
                    if extracted_keywords.matched_keywords:
                        enhanced_text = work_text + f"\n\n技术关键词：{', '.join(extracted_keywords.matched_keywords[:3])}"
                        suggestions.append(EditSuggestion(
                            section=f"工作经历{i+1}",
                            original_text=work_text,
                            suggested_text=enhanced_text,
                            reason="突出相关技术关键词",
                            priority="low"
                        ))
            except Exception as e:
                print(f"工作经历建议生成失败: {e}")
                # 不添加任何建议，保持原文
                continue
        
        return suggestions
    
    async def _suggest_project_improvements(self, projects: List[Dict[str, Any]], extracted_keywords: ExtractedKeywords, job_hc: str) -> List[EditSuggestion]:
        suggestions = []
        
        for i, project in enumerate(projects):
            project_text = project.get('raw_text', '')
            if not project_text:
                continue
            
            # 只做基础的格式和表达优化，不添加虚构内容
            prompt = f"""
            当前项目经历描述：
            {project_text}
            
            岗位要求：
            {job_hc}
            
            请对这个项目描述进行表达优化，要求：
            1. 保持所有事实内容不变，不添加任何虚构信息
            2. 优化语言表达，使其更专业和简洁
            3. 调整句式结构，突出技术亮点和个人贡献
            4. 如果内容中提到的技术与岗位要求匹配，可以适当强调
            5. 绝对不能编造技术栈、项目成果、数据指标或业务背景
            
            请以JSON格式返回：
            {{"improved_text": "优化后的文本", "reason": "优化原因"}}
            """
            
            try:
                response = await self._call_openai(prompt)
                if response:  # 如果API调用成功
                    suggestion_data = self._parse_json_response(response)
                    
                    if suggestion_data.get("improved_text"):
                        # 验证优化内容是否过于偏离原文
                        original_length = len(project_text)
                        improved_length = len(suggestion_data["improved_text"])
                        
                        # 如果优化后的内容长度增加超过40%，可能包含虚构内容
                        if improved_length > original_length * 1.4:
                            continue
                        
                        suggestions.append(EditSuggestion(
                            section=f"项目经历{i+1}",
                            original_text=project_text,
                            suggested_text=suggestion_data["improved_text"],
                            reason=suggestion_data.get("reason", "优化项目描述表达"),
                            priority="medium"
                        ))
                else:
                    # API调用失败时，只做基础的关键词优化
                    if extracted_keywords.matched_keywords:
                        enhanced_text = project_text + f"\n\n相关技术：{', '.join(extracted_keywords.matched_keywords[:3])}"
                        suggestions.append(EditSuggestion(
                            section=f"项目经历{i+1}",
                            original_text=project_text,
                            suggested_text=enhanced_text,
                            reason="突出相关技术栈",
                            priority="low"
                        ))
            except Exception as e:
                print(f"项目经历建议生成失败: {e}")
                # 不添加任何建议，保持原文
                continue
        
        return suggestions
    
    async def _apply_optimizations(self, parsed_resume: ParsedResume, suggestions: List[EditSuggestion], job_hc: str) -> str:
        # 构建优化后的简历内容
        optimized_sections = []
        
        # 个人信息
        if parsed_resume.personal_info:
            personal_section = self._format_personal_info(parsed_resume.personal_info)
            optimized_sections.append(personal_section)
        
        # 技能（应用建议）
        if parsed_resume.skills or any(s.section == "技能" for s in suggestions):
            skills_section = await self._apply_skills_optimizations(parsed_resume.skills, suggestions)
            optimized_sections.append(skills_section)
        
        # 工作经历（应用建议）
        if parsed_resume.work_experience or any("工作经历" in s.section for s in suggestions):
            work_section = await self._apply_work_optimizations(parsed_resume.work_experience, suggestions)
            optimized_sections.append(work_section)
        
        # 项目经历（应用建议）
        if parsed_resume.projects or any("项目经历" in s.section for s in suggestions):
            projects_section = await self._apply_projects_optimizations(parsed_resume.projects, suggestions)
            optimized_sections.append(projects_section)
        
        # 教育经历
        if parsed_resume.education:
            education_section = self._format_education(parsed_resume.education)
            optimized_sections.append(education_section)
        
        # 如果没有任何内容，添加一个基本结构
        if not optimized_sections:
            optimized_sections = [
                "# 个人简历",
                "## 专业技能",
                "- 待完善",
                "## 工作经历", 
                "待补充",
                "## 项目经历",
                "待补充",
                "## 教育经历",
                "待补充"
            ]
        
        return "\n\n".join(optimized_sections)
    
    def _format_personal_info(self, personal_info: Dict[str, Any]) -> str:
        lines = ["# 个人信息"]
        
        # 只显示关键信息，避免重复
        if personal_info.get("name"):
            lines.append(f"**姓名：** {personal_info['name']}")
        
        contact_items = []
        if personal_info.get("phone"):
            contact_items.append(f"📞 {personal_info['phone']}")
        if personal_info.get("email"):
            contact_items.append(f"📧 {personal_info['email']}")
        if personal_info.get("address"):
            contact_items.append(f"📍 {personal_info['address']}")
        
        if contact_items:
            lines.append(f"**联系方式：** {' | '.join(contact_items)}")
        
        if personal_info.get("role"):
            lines.append(f"**职位：** {personal_info['role']}")
        
        return "\n".join(lines)
    
    async def _apply_skills_optimizations(self, skills: List[str], suggestions: List[EditSuggestion]) -> str:
        skills_suggestions = [s for s in suggestions if s.section == "技能"]
        
        if skills_suggestions:
            # 使用建议中的优化技能
            optimized_skills = []
            for suggestion in skills_suggestions:
                optimized_skills.append(suggestion.suggested_text)
            skills_text = "\n".join([f"- {skill}" for skill in optimized_skills])
        else:
            # 使用原始技能
            skills_text = "\n".join([f"- {skill}" for skill in skills]) if skills else "- 待完善"
        
        return f"## 专业技能\n{skills_text}"
    
    async def _apply_work_optimizations(self, work_experience: List[Dict[str, Any]], suggestions: List[EditSuggestion]) -> str:
        section_lines = ["## 工作经历"]
        
        for i, work in enumerate(work_experience):
            work_suggestions = [s for s in suggestions if s.section == f"工作经历{i+1}"]
            
            if work_suggestions:
                # 使用优化后的文本
                section_lines.append(work_suggestions[0].suggested_text)
            else:
                # 使用原始文本或构建文本
                work_text = work.get('raw_text', '')
                if not work_text:
                    # 如果没有raw_text，从字段构建
                    work_parts = []
                    if work.get('period'):
                        work_parts.append(f"**{work['period']}**")
                    if work.get('position') and work.get('company'):
                        work_parts.append(f"**{work['position']}** | {work['company']}")
                    elif work.get('position'):
                        work_parts.append(f"**{work['position']}**")
                    elif work.get('company'):
                        work_parts.append(f"**{work['company']}**")
                    
                    if work.get('responsibilities'):
                        for resp in work['responsibilities']:
                            work_parts.append(f"- {resp}")
                    
                    work_text = "\n".join(work_parts)
                
                section_lines.append(work_text)
            
            section_lines.append("")  # 添加空行分隔
        
        return "\n".join(section_lines)
    
    async def _apply_projects_optimizations(self, projects: List[Dict[str, Any]], suggestions: List[EditSuggestion]) -> str:
        section_lines = ["## 项目经历"]
        
        for i, project in enumerate(projects):
            project_suggestions = [s for s in suggestions if s.section == f"项目经历{i+1}"]
            
            if project_suggestions:
                # 使用优化后的文本
                project_content = project_suggestions[0].suggested_text
            else:
                # 使用原始文本或构建文本
                project_text = project.get('raw_text', '')
                if not project_text:
                    # 如果没有raw_text，从字段构建
                    project_parts = []
                    if project.get('name'):
                        project_parts.append(f"### {project['name']}")
                    if project.get('period'):
                        project_parts.append(f"**时间：** {project['period']}")
                    if project.get('technologies'):
                        project_parts.append(f"**技术栈：** {project['technologies']}")
                    
                    if project.get('description'):
                        if isinstance(project['description'], list):
                            for desc in project['description']:
                                project_parts.append(f"- {desc}")
                        else:
                            project_parts.append(f"- {project['description']}")
                    
                    project_content = "\n".join(project_parts)
                else:
                    project_content = project_text
            
            # 确保项目有标题
            if project_content and not project_content.strip().startswith('#'):
                # 尝试从内容中提取项目名称作为标题
                project_name = f"项目{i+1}"
                
                # 查找系统名称
                system_matches = re.findall(r'([A-Za-z]+\s*[系统|平台|项目])', project_content)
                if system_matches:
                    project_name = system_matches[0]
                elif project.get('name'):
                    project_name = project['name']
                
                # 添加项目标题
                section_lines.append(f"### {project_name}")
                section_lines.append(project_content)
            else:
                section_lines.append(project_content)
            
            section_lines.append("")  # 添加空行分隔
        
        return "\n".join(section_lines)
    
    def _format_education(self, education: List[Dict[str, Any]]) -> str:
        section_lines = ["## 教育经历"]
        
        for edu in education:
            edu_text = edu.get('raw_text', '')
            if not edu_text:
                # 如果没有raw_text，从字段构建
                edu_parts = []
                if edu.get('period'):
                    edu_parts.append(f"**{edu['period']}**")
                if edu.get('school'):
                    edu_parts.append(f"**{edu['school']}**")
                if edu.get('major'):
                    edu_parts.append(f"专业：{edu['major']}")
                
                edu_text = " | ".join(edu_parts) if edu_parts else "教育信息"
            
            section_lines.append(edu_text)
            section_lines.append("")
        
        return "\n".join(section_lines)
    
    async def _generate_improvement_summary(self, suggestions: List[EditSuggestion]) -> str:
        if not suggestions:
            return "无需改进建议"
        
        summary_parts = []
        summary_parts.append(f"共生成 {len(suggestions)} 条优化建议：")
        
        high_priority = [s for s in suggestions if s.priority == "high"]
        medium_priority = [s for s in suggestions if s.priority == "medium"]
        
        if high_priority:
            summary_parts.append(f"高优先级建议 {len(high_priority)} 条")
        if medium_priority:
            summary_parts.append(f"中优先级建议 {len(medium_priority)} 条")
        
        summary_parts.append("主要改进方向：技能描述优化、工作成果量化、关键词匹配提升")
        
        return "\n".join(summary_parts)
    
    async def _call_openai(self, prompt: str) -> str:
        if not self.client:
            return ""  # 如果没有AI客户端，直接返回空字符串
        
        try:
            response = self.client.chat.completions.create(
                model=settings.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            # 返回空字符串，让调用方使用备用逻辑
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