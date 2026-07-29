from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from managers.match_manager import MatchManager
from database import SessionLocal

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/match/{match_code}")
async def match_page(request: Request, match_code: str):

    async with SessionLocal() as session:

        state = await MatchManager.get_match_state(
            session=session,
            match_code=match_code,
            request=request
        )

        return templates.TemplateResponse(
            "match.html",
            {
                "request": request,
                **state
            }
        )