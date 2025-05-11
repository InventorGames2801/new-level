from fastapi.templating import Jinja2Templates
from pathlib import Path

# Получаем абсолютный путь к директории templates
templates_dir = Path(__file__).parent.parent / "templates"

# Инициализируем шаблонизатор Jinja2
templates = Jinja2Templates(directory=str(templates_dir))