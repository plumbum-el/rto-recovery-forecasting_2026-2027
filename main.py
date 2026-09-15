from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="RTO Forecasting App")


app.mount(
    "/rto-forecast_first_lab_static",
    StaticFiles(directory="rto-forecast_first_lab_static"),
    name="static"
)
templates = Jinja2Templates(directory="rto-forecast_first_lab_templates")


MINIO_URL = "http://localhost:9000/rto-forecast-media"

SERVICES = [
    {
        "id": 1,
        "title": "Синхронная",
        "description": "Мгновенная репликация данных с минимальным RTO.",
        "estimated_time": 5,
        "rpo_time": 0,
        "cost": 1200,
        "status": "published",
        "image_key": f"{MINIO_URL}/sync_image.png",
        "video_key": f"{MINIO_URL}/sync_video.mp4"
    },
    {
        "id": 2,
        "title": "Асинхронная",
        "description": "Периодическая синхронизация с задержкой до 1 часа.",
        "estimated_time": 60,
        "rpo_time": 15,
        "cost": 600,
        "status": "published",
        "image_key": f"{MINIO_URL}/async_image.png",
        "video_key": f"{MINIO_URL}/async_video.mp4"
    },
    {
        "id": 3,
        "title": "Бэкап в Cloud",
        "description": "Автоматическое резервное копирование в облачное хранилище.",
        "estimated_time": 240,
        "rpo_time": 60,
        "cost": 150,
        "status": "published",
        "image_key": f"{MINIO_URL}/cloud_image.png",
        "video_key": f"{MINIO_URL}/cloud_video.mp4"
    },
    {
        "id": 4,
        "title": "Холодный резерв",
        "description": "Ручное восстановление через Hetman / R-Studio.",
        "estimated_time": 1440,
        "rpo_time": 240,
        "cost": 50,
        "status": "draft",
        "image_key": f"{MINIO_URL}/cold_image.png",
        "video_key": f"{MINIO_URL}/cold_video.mp4"
    }
]

@app.get("/")
@app.get("/feed")
def get_feed(request: Request, id: int = 1, next: bool = False):
    published_services = [s for s in SERVICES if s["status"] == "published"]

    current_index = 0
    for idx, s in enumerate(published_services):
        if s["id"] == id:
            current_index = idx
            break

    if next:
        current_index = (current_index + 1) % len(published_services)

    current_service = published_services[current_index]

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={
            "service": current_service
        }
    )

@app.get("/draft")
def get_draft(request: Request):
    draft_service = next((s for s in SERVICES if s["status"] == "draft"), SERVICES[-1])
    return templates.TemplateResponse(
        request=request,
        name="draft.html",
        context={
            "service": draft_service
        }
    )

@app.get("/catalog")
def get_catalog(request: Request, query: str = None):
    filtered_services = SERVICES
    if query:
        filtered_services = [
            s for s in SERVICES
            if query.lower() in s["title"].lower() or query.lower() in s["description"].lower()
        ]

    return templates.TemplateResponse(
        request=request,
        name="catalog.html",
        context={
            "services": filtered_services,
            "query": query or ""
        }
    )
