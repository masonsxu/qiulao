import markdown
from jinja2 import Environment, BaseLoader
from datetime import datetime
from typing import Dict, Any
from app.models.schemas import EditedResume, RenderedResume

class ResumeRendererService:
    def __init__(self):
        self.md = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])
        self.jinja_env = Environment(loader=BaseLoader())
        
    async def render_resume(self, edited_resume: EditedResume) -> RenderedResume:
        # 将markdown转换为HTML
        html_content = self._markdown_to_html(edited_resume.content)
        
        # 应用CSS样式
        styled_html = self._apply_styling(html_content)
        
        return RenderedResume(
            html_content=styled_html,
            markdown_content=edited_resume.content,
            pdf_url=None,  # 可以后续集成PDF生成
            created_at=datetime.now()
        )
    
    def _markdown_to_html(self, markdown_content: str) -> str:
        # 转换markdown为HTML
        html = self.md.convert(markdown_content)
        return html
    
    def _apply_styling(self, html_content: str) -> str:
        # 现代简历CSS样式
        css_styles = """
        <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }
        
        .resume-container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        
        h2 {
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        h3 {
            color: #2c3e50;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .contact-info {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        
        .contact-info ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }
        
        .contact-info li {
            background: white;
            padding: 8px 15px;
            border-radius: 20px;
            border: 1px solid #bdc3c7;
        }
        
        .skills {
            margin-bottom: 30px;
        }
        
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .skill-category {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        
        .skill-category h4 {
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 1em;
            font-weight: bold;
        }
        
        .skill-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .skill-tag {
            background: #3498db;
            color: white;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            white-space: nowrap;
        }
        
        .skill-tag.primary {
            background: #e74c3c;
        }
        
        .skill-tag.secondary {
            background: #27ae60;
        }
        
        .skill-tag.tool {
            background: #f39c12;
        }
        
        /* 备用：原始列表样式 */
        .skills ul {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            list-style: none;
            padding: 0;
            margin: 10px 0;
        }
        
        .skills li {
            background: #3498db;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin: 0;
        }
        
        .skills p {
            margin: 0;
            padding: 0;
        }
        
        .work-experience, .projects {
            margin-bottom: 30px;
        }
        
        .job-title {
            font-weight: bold;
            color: #2c3e50;
            font-size: 1.2em;
        }
        
        .company {
            color: #7f8c8d;
            font-style: italic;
        }
        
        .period {
            color: #95a5a6;
            float: right;
            font-size: 0.9em;
        }
        
        .responsibilities {
            margin-top: 10px;
        }
        
        .responsibilities li {
            margin-bottom: 5px;
            position: relative;
            padding-left: 20px;
        }
        
        .responsibilities li:before {
            content: "▸";
            color: #3498db;
            font-weight: bold;
            position: absolute;
            left: 0;
        }
        
        .education {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #27ae60;
        }
        
        .project-item {
            background: #f8f9fa;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            border-left: 4px solid #e74c3c;
        }
        
        .tech-stack {
            background: #2c3e50;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            display: inline-block;
            margin: 5px 5px 5px 0;
        }
        
        @media print {
            body {
                background: white;
                padding: 0;
            }
            .resume-container {
                box-shadow: none;
                padding: 20px;
            }
        }
        
        @media (max-width: 768px) {
            .contact-info ul {
                flex-direction: column;
            }
            .period {
                float: none;
                display: block;
                margin-top: 5px;
            }
        }
        </style>
        """
        
        # 创建完整的HTML文档
        full_html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>个人简历</title>
            {css_styles}
        </head>
        <body>
            <div class="resume-container">
                {self._enhance_html_structure(html_content)}
            </div>
            <script>
                /* 简单的交互功能 */
                document.addEventListener('DOMContentLoaded', function() {{
                    /* 为技能添加hover效果 */
                    const skills = document.querySelectorAll('.skills li');
                    skills.forEach(skill => {{
                        skill.addEventListener('mouseenter', function() {{
                            this.style.transform = 'scale(1.05)';
                            this.style.transition = 'transform 0.2s ease';
                        }});
                        skill.addEventListener('mouseleave', function() {{
                            this.style.transform = 'scale(1)';
                        }});
                    }});
                }});
            </script>
        </body>
        </html>
        """
        
        return full_html
    
    def _enhance_html_structure(self, html_content: str) -> str:
        import re
        
        # 增强HTML结构，添加CSS类
        enhanced_html = html_content
        
        # 为不同部分添加CSS类
        enhanced_html = enhanced_html.replace('<h2>个人信息</h2>', '<h2 class="section-title">个人信息</h2>')
        enhanced_html = enhanced_html.replace('<h2>联系方式</h2>', '<h2 class="section-title">联系方式</h2>')
        enhanced_html = enhanced_html.replace('<h2>专业技能</h2>', '<h2 class="section-title">专业技能</h2>')
        enhanced_html = enhanced_html.replace('<h2>工作经历</h2>', '<h2 class="section-title">工作经历</h2>')
        enhanced_html = enhanced_html.replace('<h2>项目经历</h2>', '<h2 class="section-title">项目经历</h2>')
        enhanced_html = enhanced_html.replace('<h2>教育经历</h2>', '<h2 class="section-title">教育经历</h2>')
        
        # 识别并格式化联系信息
        if '个人信息' in enhanced_html or '联系方式' in enhanced_html:
            # 查找联系信息部分并添加特殊样式
            contact_pattern = r'(<h2[^>]*>(?:个人信息|联系方式)</h2>.*?</ul>)'
            enhanced_html = re.sub(contact_pattern, r'<div class="contact-info">\1</div>', enhanced_html, flags=re.DOTALL)
        
        # 为技能部分添加特殊样式和结构
        if '专业技能' in enhanced_html or '技能' in enhanced_html:
            # 找到技能部分
            skills_pattern = r'(<h2[^>]*>(?:专业技能|技能)</h2>)(.*?)(?=<h2|$)'
            match = re.search(skills_pattern, enhanced_html, flags=re.DOTALL)
            if match:
                skills_title = match.group(1)
                skills_content = match.group(2).strip()
                
                # 解析技能列表
                skill_items = re.findall(r'<li>(.*?)</li>', skills_content, flags=re.DOTALL)
                
                if skill_items:
                    # 分类技能
                    categorized_skills = self._categorize_skills(skill_items)
                    
                    # 生成新的技能HTML结构
                    enhanced_skills = f'{skills_title}\n<div class="skills-grid">\n'
                    
                    for category, skills in categorized_skills.items():
                        enhanced_skills += f'''
                        <div class="skill-category">
                            <h4>{category}</h4>
                            <div class="skill-tags">
                        '''
                        
                        for skill in skills:
                            # 根据技能类型设置不同的标签样式
                            tag_class = self._get_skill_tag_class(skill, category)
                            enhanced_skills += f'<span class="skill-tag {tag_class}">{skill}</span>\n'
                        
                        enhanced_skills += '''
                            </div>
                        </div>
                        '''
                    
                    enhanced_skills += '</div>'
                    
                    # 包装整个技能部分
                    final_skills = f'<div class="skills">{enhanced_skills}</div>'
                    
                    # 替换原内容
                    original_section = skills_title + skills_content
                    enhanced_html = enhanced_html.replace(original_section, final_skills)
                else:
                    # 如果没有找到技能列表，使用原始方法
                    skills_pattern = r'(<h2[^>]*>(?:专业技能|技能)</h2>.*?</ul>)'
                    match = re.search(skills_pattern, enhanced_html, flags=re.DOTALL)
                    if match:
                        skills_section = match.group(1)
                        enhanced_skills = f'<div class="skills">{skills_section}</div>'
                        enhanced_html = enhanced_html.replace(skills_section, enhanced_skills)
        
        # 优化项目经历部分结构
        if '项目经历' in enhanced_html:
            # 找到项目部分的内容
            project_pattern = r'<h2[^>]*>项目经历</h2>(.*?)(?=<h2|$)'
            match = re.search(project_pattern, enhanced_html, flags=re.DOTALL)
            if match:
                project_content = match.group(1).strip()
                # 将段落转换为项目项
                paragraphs = re.findall(r'<p>(.*?)</p>', project_content, flags=re.DOTALL)
                
                enhanced_projects = '<h2 class="section-title">项目经历</h2>\n'
                for i, para in enumerate(paragraphs, 1):
                    if para.strip():
                        # 尝试从内容中提取项目名称
                        project_name = f"项目 {i}"
                        if "系统" in para[:50]:
                            name_match = re.search(r'([^，。]*系统[^，。]*)', para[:100])
                            if name_match:
                                project_name = name_match.group(1).strip()
                        
                        enhanced_projects += f'''
                        <div class="project-item">
                            <h3>{project_name}</h3>
                            <p>{para}</p>
                        </div>
                        '''
                
                # 替换原内容
                original_section = f'<h2 class="section-title">项目经历</h2>{project_content}'
                enhanced_html = enhanced_html.replace(original_section, enhanced_projects)
        
        return enhanced_html
    
    def _categorize_skills(self, skill_items):
        """将技能分类"""
        categories = {
            "编程语言": [],
            "框架&工具": [],
            "数据库": [],
            "架构&设计": [],
            "运维&部署": []
        }
        
        # 定义关键词映射
        keywords_map = {
            "编程语言": ["Golang", "Python", "Java", "JavaScript", "C++", "TypeScript", "编程", "语言"],
            "框架&工具": ["go-zero", "Kratos", "Flask", "Django", "React", "Vue", "框架", "库"],
            "数据库": ["MySQL", "MongoDB", "Redis", "PostgreSQL", "数据库", "数据建模", "事务"],
            "架构&设计": ["微服务", "架构", "设计", "DDD", "领域", "分布式", "高并发", "系统"],
            "运维&部署": ["Docker", "Kubernetes", "CI/CD", "容器", "部署", "运维", "监控", "可观测性"]
        }
        
        for skill in skill_items:
            skill = skill.strip()
            categorized = False
            
            # 根据关键词分类
            for category, keywords in keywords_map.items():
                if any(keyword in skill for keyword in keywords):
                    categories[category].append(skill)
                    categorized = True
                    break
            
            # 如果没有分类，放入框架&工具
            if not categorized:
                categories["框架&工具"].append(skill)
        
        # 移除空的分类
        return {k: v for k, v in categories.items() if v}
    
    def _get_skill_tag_class(self, skill, category):
        """根据技能和分类返回CSS类"""
        if category == "编程语言":
            return "primary"
        elif category == "架构&设计":
            return "secondary"
        elif category == "运维&部署":
            return "tool"
        else:
            return ""
    
    def generate_pdf_url(self, html_content: str) -> str:
        # 预留PDF生成功能
        # 可以集成wkhtmltopdf或puppeteer等工具
        return None
    
    def _create_template_variations(self) -> Dict[str, str]:
        """创建不同的简历模板"""
        templates = {
            "modern": "现代简洁风格",
            "professional": "商务专业风格", 
            "creative": "创意设计风格",
            "technical": "技术专业风格"
        }
        return templates
    
    async def render_with_template(self, edited_resume: EditedResume, template_name: str = "modern") -> RenderedResume:
        """使用指定模板渲染简历"""
        if template_name == "professional":
            html_content = self._render_professional_template(edited_resume.content)
        elif template_name == "creative":
            html_content = self._render_creative_template(edited_resume.content)
        elif template_name == "technical":
            html_content = self._render_technical_template(edited_resume.content)
        else:
            html_content = self._markdown_to_html(edited_resume.content)
            html_content = self._apply_styling(html_content)
        
        return RenderedResume(
            html_content=html_content,
            markdown_content=edited_resume.content,
            pdf_url=None,
            created_at=datetime.now()
        )
    
    def _render_professional_template(self, markdown_content: str) -> str:
        # 商务风格模板 - 更保守的设计
        html = self._markdown_to_html(markdown_content)
        # 应用商务风格CSS
        professional_css = """
        <style>
        body { font-family: 'Times New Roman', serif; color: #000; }
        h1 { color: #000; border-bottom: 2px solid #000; }
        h2 { color: #333; border-left: 3px solid #333; }
        .skills li { background: #333; }
        </style>
        """
        return f"<!DOCTYPE html><html><head>{professional_css}</head><body><div class='resume-container'>{html}</div></body></html>"
    
    def _render_creative_template(self, markdown_content: str) -> str:
        # 创意风格模板 - 更活泼的设计
        html = self._markdown_to_html(markdown_content)
        creative_css = """
        <style>
        body { font-family: 'Arial', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        h1 { color: #fff; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .resume-container { background: rgba(255,255,255,0.95); }
        </style>
        """
        return f"<!DOCTYPE html><html><head>{creative_css}</head><body><div class='resume-container'>{html}</div></body></html>"
    
    def _render_technical_template(self, markdown_content: str) -> str:
        # 技术风格模板 - 代码风格设计
        html = self._markdown_to_html(markdown_content)
        technical_css = """
        <style>
        body { font-family: 'Consolas', 'Monaco', monospace; background: #1e1e1e; color: #d4d4d4; }
        .resume-container { background: #2d2d30; border: 1px solid #3e3e42; }
        h1 { color: #569cd6; }
        h2 { color: #4ec9b0; border-left: 4px solid #4ec9b0; }
        </style>
        """
        return f"<!DOCTYPE html><html><head>{technical_css}</head><body><div class='resume-container'>{html}</div></body></html>"