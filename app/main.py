from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from app.api import resume_parser, keyword_extractor, resume_editor, resume_renderer, optimization
from app.core.config import settings

app = FastAPI(
    title="求捞 - AI简历优化系统",
    description="智能简历优化系统，帮助用户根据岗位HC自动优化简历",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="templates")

app.include_router(resume_parser.router, prefix="/api/v1", tags=["简历解析"])
app.include_router(keyword_extractor.router, prefix="/api/v1", tags=["关键字提取"])
app.include_router(resume_editor.router, prefix="/api/v1", tags=["简历编辑"])
app.include_router(resume_renderer.router, prefix="/api/v1", tags=["简历渲染"])
app.include_router(optimization.router, prefix="/api/v1", tags=["完整优化流程"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.svg", media_type="image/svg+xml")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "服务运行正常"}