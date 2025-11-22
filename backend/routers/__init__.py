from .profile import router as profile_router
from .learning_path import router as learning_path_router
from .content import router as content_router
from .missions import router as missions_router
from .progress import router as progress_router
from .chatbot import router as chatbot_router
from .auth import router as auth_router
from .mentor import router as mentor_router
from .module_progress import router as module_progress_router
from .courses import router as courses_router

__all__ = [
    "profile_router",
    "learning_path_router",
    "content_router",
    "missions_router",
    "progress_router",
    "chatbot_router",
    "auth_router",
    "mentor_router",
    "module_progress_router",
    "courses_router"
]

