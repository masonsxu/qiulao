import asyncio
import sys
sys.path.append('.')
from app.services.resume_parser import ResumeParserService
from app.services.keyword_extractor import KeywordExtractorService
from app.services.resume_editor import ResumeEditorService
from app.services.resume_renderer import ResumeRendererService

async def test_pipeline():
    # Read the debug resume
    with open('debug_resume.md', 'r', encoding='utf-8') as f:
        resume_content = f.read()
    
    # Parse the resume
    parser = ResumeParserService()
    parsed = parser.parse_markdown_resume(resume_content)
    print(f'Parsed resume - Name: {parsed.personal_info.get("name")}, Skills: {len(parsed.skills)}, Work: {len(parsed.work_experience)}')
    
    # Extract keywords (using a simple job description)
    job_hc = '前端开发工程师，要求熟悉React、Vue、TypeScript、Webpack等前端技术栈'
    extractor = KeywordExtractorService()
    keywords = await extractor.extract_keywords(parsed, job_hc)
    print(f'Keywords - Matched: {len(keywords.matched_keywords)}, Missing: {len(keywords.missing_keywords)}')
    
    # Edit the resume (this should NOT add fabricated content)
    editor = ResumeEditorService()
    edited = await editor.edit_resume(parsed, keywords, job_hc)
    print(f'Editing complete - {len(edited.suggestions)} suggestions generated')
    
    # Check if work experience was fabricated
    print('\n=== Work Experience Content Check ===')
    original_work_text = ''.join([work.get('raw_text', '') for work in parsed.work_experience])
    print(f'Original work content length: {len(original_work_text)}')
    print(f'Edited content length: {len(edited.content)}')
    
    # Look for signs of fabrication in the edited content
    if '虚构' in edited.content or len(edited.content) > len(resume_content) * 2:
        print('WARNING: Possible fabricated content detected!')
    else:
        print('Content appears to be factual optimization only')
    
    # Save the test result
    with open('test_optimized_resume.html', 'w', encoding='utf-8') as f:
        renderer = ResumeRendererService()
        rendered = await renderer.render_resume(edited)
        f.write(rendered.html_content)
    print('Test result saved to test_optimized_resume.html')

if __name__ == '__main__':
    asyncio.run(test_pipeline())