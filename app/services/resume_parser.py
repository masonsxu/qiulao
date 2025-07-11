import re
import markdown
from typing import Dict, List, Any
from app.models.schemas import ParsedResume

class ResumeParserService:
    def __init__(self):
        self.md = markdown.Markdown(extensions=['tables', 'fenced_code'])
    
    def parse_markdown_resume(self, markdown_content: str) -> ParsedResume:
        print(f"开始解析简历，内容长度: {len(markdown_content)}")
        print(f"简历前500字符: {markdown_content[:500]}")
        
        sections = self._split_into_sections(markdown_content)
        
        personal_info = self._extract_personal_info(sections)
        education = self._extract_education(sections)
        work_experience = self._extract_work_experience(sections)
        skills = self._extract_skills(sections)
        projects = self._extract_projects(sections)
        
        print(f"解析结果统计: personal_info={len(personal_info)}, education={len(education)}, work_experience={len(work_experience)}, skills={len(skills)}, projects={len(projects)}")
        
        return ParsedResume(
            personal_info=personal_info,
            education=education,
            work_experience=work_experience,
            skills=skills,
            projects=projects,
            raw_sections=sections
        )
    
    def _split_into_sections(self, content: str) -> Dict[str, str]:
        sections = {}
        current_section = "header"
        current_content = []
        
        lines = content.split('\n')
        for line in lines:
            line_stripped = line.strip()
            
            # 检查是否是标题行（以一个或多个#开头，或者包含特定的section关键词）
            is_title = False
            section_title = ""
            
            if line_stripped.startswith('#'):
                # 标准markdown标题
                section_title = line_stripped.lstrip('#').strip().lower()
                is_title = True
            elif line_stripped.startswith('**') and line_stripped.endswith('**'):
                # 粗体标题，例如 **核心技术栈**
                section_title = line_stripped.strip('*').strip().lower()
                is_title = True
            elif any(keyword in line_stripped for keyword in ['技术栈', '工作经历', '项目', '教育', '技能', '个人信息', '职业', '成就']):
                # 包含关键词的行
                section_title = line_stripped.lower()
                is_title = True
            
            if is_title and section_title:
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                current_section = section_title
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        print(f"解析到的sections: {list(sections.keys())}")
        for key, value in sections.items():
            print(f"Section '{key}': {value[:100]}..." if len(value) > 100 else f"Section '{key}': {value}")
        
        return sections
    
    def _extract_personal_info(self, sections: Dict[str, str]) -> Dict[str, Any]:
        personal_info = {}
        
        # 尝试多种可能的section名称
        header_content = ""
        for key in sections.keys():
            if any(keyword in key for keyword in ["个人信息", "联系方式", "header", "基本信息"]) or key == "header":
                header_content += sections[key] + "\n"
        
        # 如果没有找到专门的个人信息section，使用header或第一个section
        if not header_content:
            if "header" in sections:
                header_content = sections["header"]
            elif sections:
                # 使用第一个section作为header
                first_key = list(sections.keys())[0]
                header_content = sections[first_key]
        
        # 首先提取邮箱和电话（避免被误认为姓名）
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'1[3-9]\d{9}'
        
        email_match = re.search(email_pattern, header_content)
        phone_match = re.search(phone_pattern, header_content)
        
        if email_match:
            personal_info["email"] = email_match.group()
        if phone_match:
            personal_info["phone"] = phone_match.group()
        
        # 提取地址（寻找地名）
        location_patterns = [
            r'📍\s*([^\|]+)',  # 📍厦门
            r'地址[：:]\s*([^\n\|]+)',
            r'([北京|上海|广州|深圳|杭州|厦门|福州|成都|武汉|重庆|南京|苏州|天津|西安|郑州|长沙|青岛|大连|宁波|无锡|佛山|烟台|东莞|南通|唐山|泉州|常州|石家庄|济南|温州|绍兴|嘉兴|太原|贵阳|昆明|兰州|银川|西宁|乌鲁木齐|拉萨|呼和浩特|南宁|海口|哈尔滨|长春|沈阳][^|\n]*)'
        ]
        
        for pattern in location_patterns:
            location_match = re.search(pattern, header_content)
            if location_match:
                location = location_match.group(1).strip()
                # 清理地址中的emoji和多余字符
                location = re.sub(r'[📍|｜\s]+', '', location).strip()
                if location:
                    personal_info["address"] = location
                break
        
        # 提取姓名（排除联系方式行）
        lines = header_content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 跳过包含邮箱、电话、地址符号的行
            if any(char in line for char in ['@', '📞', '📧', '📍', '|', '｜']) and len(line) > 20:
                continue
                
            if line.startswith('###') and '**' in line:
                # 处理 ### **徐俊飞** 这种格式
                name_match = re.search(r'\*\*(.*?)\*\*', line)
                if name_match:
                    name = name_match.group(1).strip()
                    # 确保姓名不包含特殊字符
                    if not re.search(r'[@📞📧📍|｜\d]', name) and len(name) <= 10:
                        personal_info["name"] = name
            elif line and i < 3 and not line.startswith('#') and not line.startswith('**'):
                # 前几行的简短文本可能是姓名，但要排除联系方式
                if len(line) <= 10 and not re.search(r'[@📞📧📍|｜\d]', line):
                    personal_info["name"] = line.strip()
        
        # 提取职位/角色
        role_patterns = [
            r'技术架构师',
            r'架构师',
            r'工程师',
            r'开发[者|人员]?',
            r'经理',
            r'总监'
        ]
        
        for pattern in role_patterns:
            role_match = re.search(pattern, header_content)
            if role_match:
                personal_info["role"] = role_match.group()
                break
        
        return personal_info
    
    def _extract_education(self, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        education_content = ""
        for key in sections.keys():
            if any(keyword in key for keyword in ["教育经历", "学历", "教育背景", "教育"]):
                education_content += sections[key] + "\n"
        
        if not education_content:
            return []
        
        education_list = []
        entries = re.split(r'\n\s*\n', education_content.strip())
        
        for entry in entries:
            if entry.strip():
                education_item = self._parse_education_entry(entry)
                if education_item:
                    education_list.append(education_item)
        
        return education_list
    
    def _parse_education_entry(self, entry: str) -> Dict[str, Any]:
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        if not lines:
            return {}
        
        education_item = {"raw_text": entry}
        
        for line in lines:
            if re.search(r'\d{4}', line):
                education_item["period"] = line
            elif any(keyword in line for keyword in ["大学", "学院", "学校"]):
                education_item["school"] = line
            elif any(keyword in line for keyword in ["专业", "学位"]):
                education_item["major"] = line
        
        return education_item
    
    def _extract_work_experience(self, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        work_content = ""
        work_sections = []
        
        # 收集所有工作相关的sections
        for key in sections.keys():
            if any(keyword in key for keyword in ["工作经历", "工作经验", "实习经历", "职业经历"]):
                work_content += sections[key] + "\n"
            elif any(keyword in key for keyword in ["高级前端工程师", "前端开发工程师", "架构师", "工程师", "经理", "总监"]) and "|" in key:
                # 识别像 "2019-2024 | 高级前端工程师 | 阿里巴巴集团" 这样的section
                work_sections.append((key, sections[key]))
        
        work_list = []
        
        # 处理独立的工作experience sections
        for section_title, section_content in work_sections:
            combined_content = section_title + "\n" + section_content
            work_item = self._parse_work_entry_flexible(combined_content)
            if work_item:
                work_list.append(work_item)
        
        # 如果有统一的工作经历content，也处理它
        if work_content.strip():
            # 按公司分割（寻找公司名称模式）
            company_pattern = r'\*\*([^*]+)\*\*\s*\|\s*([^*\n]+)'  # **公司名** | 职位
            companies = re.finditer(company_pattern, work_content)
            
            current_pos = 0
            for match in companies:
                # 处理前一段内容（如果有）
                if match.start() > current_pos:
                    prev_content = work_content[current_pos:match.start()].strip()
                    if prev_content and len(prev_content) > 20:  # 避免很短的片段
                        work_item = self._parse_work_entry_flexible(prev_content)
                        if work_item:
                            work_list.append(work_item)
                
                # 寻找当前公司的结束位置（下一个公司开始或文本结束）
                next_match = None
                for next_company in re.finditer(company_pattern, work_content[match.end():]):
                    next_match = next_company
                    break
                
                if next_match:
                    end_pos = match.end() + next_match.start()
                else:
                    end_pos = len(work_content)
                
                # 提取当前公司的完整内容
                company_content = work_content[match.start():end_pos].strip()
                work_item = self._parse_work_entry_flexible(company_content)
                if work_item:
                    work_list.append(work_item)
                
                current_pos = end_pos
            
            # 如果没有找到公司模式，尝试按空行分割
            if not work_list and work_content.strip():
                entries = re.split(r'\n\s*\n', work_content.strip())
                for entry in entries:
                    if entry.strip() and len(entry.strip()) > 20:
                        work_item = self._parse_work_entry_flexible(entry)
                        if work_item:
                            work_list.append(work_item)
        
        return work_list
    
    def _parse_work_entry_flexible(self, entry: str) -> Dict[str, Any]:
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        if not lines:
            return {}
        
        work_item = {"raw_text": entry}
        
        # 处理 "2019-2024 | 高级前端工程师 | 阿里巴巴集团" 这种格式的第一行
        first_line = lines[0]
        if "|" in first_line:
            parts = [part.strip() for part in first_line.split("|")]
            if len(parts) >= 3:
                # 时间 | 职位 | 公司
                work_item["period"] = parts[0]
                work_item["position"] = parts[1]
                work_item["company"] = parts[2]
            elif len(parts) == 2:
                # 时间 | 职位 或 职位 | 公司
                if re.search(r'\d{4}', parts[0]):
                    work_item["period"] = parts[0]
                    work_item["position"] = parts[1]
                else:
                    work_item["position"] = parts[0]
                    work_item["company"] = parts[1]
        
        # 提取公司和职位信息（备用方法）
        for line in lines:
            # **公司名** | 职位 格式
            company_match = re.search(r'\*\*([^*]+)\*\*\s*\|\s*([^*\n]+)', line)
            if company_match:
                work_item["company"] = company_match.group(1).strip()
                work_item["position"] = company_match.group(2).strip()
                continue
            
            # 时间信息
            if re.search(r'\d{4}', line) and ('至今' in line or '-' in line or '~' in line):
                if "period" not in work_item:
                    work_item["period"] = line
                continue
            
            # 职位标题（通常包含特殊符号或格式）
            if any(keyword in line for keyword in ["架构师", "工程师", "经理", "总监", "开发", "主管"]):
                if "position" not in work_item:
                    work_item["position"] = line
        
        # 提取工作职责
        responsibilities = []
        in_responsibilities = False
        
        for line in lines[1:]:  # 跳过第一行（通常是标题）
            # 跳过公司、职位、时间信息
            if any(key in work_item and work_item[key] == line for key in ["company", "position", "period"]):
                continue
            
            # 识别职责列表的开始
            if any(keyword in line for keyword in ["技术架构", "核心贡献", "工程效能", "主要职责", "工作内容", "负责"]):
                in_responsibilities = True
                if line.strip().endswith(':') or line.strip().endswith('：'):
                    continue  # 跳过标题行
            
            # 提取具体的职责内容
            if line.startswith('-') or line.startswith('•') or line.startswith('▸'):
                responsibilities.append(line[1:].strip())
                in_responsibilities = True
            elif in_responsibilities and line and not line.startswith('#'):
                responsibilities.append(line)
            elif line.startswith('-') == False and len(line) > 10:
                # 非列表格式的职责描述
                responsibilities.append(line)
        
        if responsibilities:
            work_item["responsibilities"] = responsibilities
        
        return work_item
    
    def _extract_skills(self, sections: Dict[str, str]) -> List[str]:
        skills_content = ""
        for key in sections.keys():
            if any(keyword in key for keyword in ["技能", "专业技能", "技术栈", "核心技能", "技术能力", "核心技术栈"]):
                skills_content += sections[key] + "\n"
        
        if not skills_content:
            return []
        
        skills = []
        lines = skills_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # 处理不同格式的技能列表
                if line.startswith('▸'):
                    # ▸ **语言框架**：Golang (go-zero微服务) | Python (Flask/Asyncio)
                    skill_line = line[1:].strip()
                    if '：' in skill_line or ':' in skill_line:
                        # 提取冒号后的内容
                        skill_value = skill_line.split('：')[-1].split(':')[-1].strip()
                        if skill_value:
                            # 按分隔符分割技能
                            skill_items = re.split(r'[|｜,，、]', skill_value)
                            for item in skill_items:
                                clean_item = re.sub(r'[()（）].*?[)）]', '', item).strip()
                                if clean_item:
                                    skills.append(clean_item)
                    else:
                        skills.append(skill_line)
                elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    # 标准的项目符号格式
                    skill_text = line[1:].strip()
                    if '：' in skill_text or ':' in skill_text:
                        skill_value = skill_text.split('：')[-1].split(':')[-1].strip()
                        if skill_value:
                            skill_items = re.split(r'[,，、]', skill_value)
                            for item in skill_items:
                                if item.strip():
                                    skills.append(item.strip())
                    else:
                        skills.append(skill_text)
                elif '：' in line or ':' in line:
                    # 直接冒号分隔的格式
                    skill_value = line.split('：')[-1].split(':')[-1].strip()
                    if skill_value:
                        skill_items = re.split(r'[,，、|｜]', skill_value)
                        for item in skill_items:
                            clean_item = re.sub(r'[()（）].*?[)）]', '', item).strip()
                            if clean_item:
                                skills.append(clean_item)
                elif not any(char in line for char in ['#', '*', '▸', '-', '•']):
                    # 纯文本行
                    skills.append(line)
        
        return [skill for skill in skills if skill and len(skill) > 1]
    
    def _extract_projects(self, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        projects_content = ""
        for key in sections.keys():
            if any(keyword in key for keyword in ["项目经历", "项目经验", "项目", "项目实践"]):
                projects_content += sections[key] + "\n"
        
        if not projects_content:
            return []
        
        projects_list = []
        entries = re.split(r'\n\s*\n', projects_content.strip())
        
        for entry in entries:
            if entry.strip():
                project_item = self._parse_project_entry(entry)
                if project_item:
                    projects_list.append(project_item)
        
        return projects_list
    
    def _parse_project_entry(self, entry: str) -> Dict[str, Any]:
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        if not lines:
            return {}
        
        project_item = {"raw_text": entry}
        
        if lines:
            project_item["name"] = lines[0]
        
        for line in lines[1:]:
            if re.search(r'\d{4}', line):
                project_item["period"] = line
            elif '技术栈' in line or '技术' in line:
                project_item["technologies"] = line
        
        description_lines = []
        for line in lines[1:]:
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                description_lines.append(line[1:].strip())
        
        if description_lines:
            project_item["description"] = description_lines
        
        return project_item