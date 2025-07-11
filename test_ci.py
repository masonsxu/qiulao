#!/usr/bin/env python3
"""
Simple test script for CI/CD that doesn't require external files
"""
import sys
import os
sys.path.append('.')

# Set environment for testing
os.environ['ENABLE_AI'] = 'False'
os.environ['DEBUG'] = 'True'

def test_imports():
    """Test that all main modules can be imported"""
    try:
        from app.main import app
        print("✓ FastAPI app imported successfully")
        
        from app.services.resume_parser import ResumeParserService
        from app.services.keyword_extractor import KeywordExtractorService
        from app.services.resume_editor import ResumeEditorService
        from app.services.resume_renderer import ResumeRendererService
        print("✓ All services imported successfully")
        
        from app.models.schemas import ParsedResume, ResumeUpload
        print("✓ All models imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    try:
        from app.services.resume_parser import ResumeParserService
        
        # Simple test content
        test_content = """# 张三简历

## 个人信息
- 姓名：张三
- 邮箱：test@example.com
- 电话：13800138000

## 专业技能
- Python
- JavaScript
- React
- FastAPI

## 工作经历
### 2020-2024 | 软件工程师 | 某公司
- 开发Web应用
- 维护后端服务

## 项目经历
### 项目A
- 使用Python开发
- 前端使用React
"""
        
        parser = ResumeParserService()
        result = parser.parse_markdown_resume(test_content)
        
        # Basic assertions
        assert len(result.skills) > 0, "Should parse skills"
        assert len(result.work_experience) > 0, "Should parse work experience"
        assert result.personal_info.get('name') is not None, "Should parse personal info"
        
        print(f"✓ Parsed {len(result.skills)} skills")
        print(f"✓ Parsed {len(result.work_experience)} work experiences")
        print(f"✓ Parsed personal info for: {result.personal_info.get('name', 'Unknown')}")
        
        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running CI tests...")
    
    success = True
    
    print("\n1. Testing imports...")
    success &= test_imports()
    
    print("\n2. Testing basic functionality...")
    success &= test_basic_functionality()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()