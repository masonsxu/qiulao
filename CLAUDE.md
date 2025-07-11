# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

求捞 (Qiulao) is an AI-powered resume optimization system built with FastAPI. It helps users optimize their resumes based on job descriptions (HC - Hiring Criteria) through intelligent keyword extraction, content enhancement, and professional formatting.

## Common Development Commands

### Environment Setup
```bash
# Create and activate virtual environment with UV
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### Running the Application
```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Alternative: using main.py (from project root)
python main.py
```

### Testing
```bash
# Run the complete pipeline test
python test_pipeline.py

# API documentation available at: http://localhost:8000/docs
```

## Architecture Overview

The application follows a clean architecture pattern with clear separation of concerns:

### Core Components
- **FastAPI Application**: `app/main.py` - Main application with CORS, static files, and route registration
- **API Layer**: `app/api/` - REST endpoints for each service module
- **Services Layer**: `app/services/` - Business logic implementation
- **Models**: `app/models/schemas.py` - Pydantic models for data validation
- **Configuration**: `app/core/config.py` - Settings management with environment variables

### Service Architecture
The system implements a modular pipeline with four main services:

1. **ResumeParserService** (`resume_parser.py`): Parses Markdown resumes into structured data
2. **KeywordExtractorService** (`keyword_extractor.py`): Extracts and matches keywords from job descriptions
3. **ResumeEditorService** (`resume_editor.py`): AI-powered content optimization and enhancement
4. **ResumeRendererService** (`resume_renderer.py`): Formats optimized content into HTML/other formats

### Data Flow
```
Markdown Resume + Job HC → Parser → Keyword Extractor → Editor → Renderer → Optimized Resume
```

## Environment Configuration

Required environment variables (see `.env.example`):
- `OPENAI_API_KEY`: OpenAI API key for AI services
- `OPENAI_BASE_URL`: API base URL (default: https://api.openai.com/v1)
- `MODEL_NAME`: AI model to use (default: gpt-3.5-turbo)
- `DEBUG`: Enable debug mode (default: False)
- `ENABLE_AI`: Toggle AI features (default: True, set to False for testing without API calls)

## Development Notes

### Python Version
- Requires Python >=3.13 (specified in pyproject.toml)
- Uses UV package manager for dependency management

### API Structure
- All API endpoints use `/api/v1` prefix
- Complete optimization flow available at `/api/v1/optimize-resume`
- Individual service endpoints available for granular control

### Testing Strategy
- `test_pipeline.py` provides end-to-end testing of the complete resume optimization flow
- Includes content validation to prevent fabrication of work experience
- Generates test output files for visual verification

### Key Dependencies
- FastAPI for web framework
- OpenAI for AI services
- Pydantic for data validation
- Jinja2 for templating
- Markdown for resume parsing
- Jieba for Chinese text processing