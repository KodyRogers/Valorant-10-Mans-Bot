from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from auth import oauth

router = APIRouter()


@router.get("/login")
async def login(request: Request):
    return await oauth.discord.authorize_redirect(
        request,
        request.url_for("callback")
    )


@router.get("/auth/callback", name="callback")
async def callback(request: Request):

    token = await oauth.discord.authorize_access_token(request)

    response = await oauth.discord.get(
        "users/@me",
        token=token
    )

    user = response.json()

    request.session["discord_id"] = int(user["id"])
    request.session["username"] = user["username"]

    return RedirectResponse("/")