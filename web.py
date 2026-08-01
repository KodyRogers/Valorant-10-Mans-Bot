from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy import select

from starlette.middleware.sessions import SessionMiddleware

from config import SESSION_SECRET

from database import SessionLocal
from managers.match_manager import MatchManager
from managers.player_manager import PlayerManager
from managers.draft_manager import DraftManager
from managers.draft_timer import DraftTimer
from managers.websocket_manager import DraftConnectionManager

from models import Player
from routes.pick_request import PickRequest
from routes.login import router

import time

app = FastAPI()
draft_connections = DraftConnectionManager()

app.add_middleware(
    SessionMiddleware,
    secret_key = SESSION_SECRET
)

app.include_router(router)
templates = Jinja2Templates(directory="templates") 
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root(request: Request):
    if "discord_id" not in request.session:
        return {"logged_in": False}

    return {
        "logged_in": True,
        "discord_id": request.session["discord_id"],
        "username": request.session["username"]
    }

@app.get("/leaderboard")
async def leaderboard():

    async with SessionLocal() as session:

        result = await session.execute(
            select(Player)
        )

        players = result.scalars().all()

        leaderboard_data = []

        for player in players:

            leaderboard_data.append({
                "discord_id": player.discord_id,
                "riot_id": f"{player.riot_name}#{player.riot_tag}",
                "wins": player.wins,
                "losses": player.losses,
                "elo": player.elo
            })

        # Sort highest elo first
        leaderboard_data.sort(
            key=lambda x: x["elo"],
            reverse=True
        )

        return leaderboard_data

@app.get("/match/{match_code}")
async def match_info(match_code: str, request: Request, start_timer: bool = False):

    async with SessionLocal() as session:

        match = await MatchManager.getMatch(session, match_code)

        if not match:
            return {"error": "Match not found."}

        match_players = await MatchManager.get_match_players(
            session,
            match.match_id
        )

        match_players = await MatchManager.get_match_players(
            session,
            match.match_id
        )
        
        team1 = []
        team2 = []
        available_players = []

        discord_ids = []

        for player in match_players:

            riot = await PlayerManager.get_riot_account_info(
                player.discord_id
            )

            if not riot:
                continue

            discord_ids.append(str(player.discord_id))

            player_data = {

                "discord_id": player.discord_id,

                "riot_name": riot["riot_name"],
                "riot_tag": riot["riot_tag"],

                "rank": riot.get("rank", "Unknown"),

                "team": player.team,

                "is_captain": player.is_captain

            }

            if player.team == 1:

                team1.append(player_data)

            elif player.team == 2:

                team2.append(player_data)

            else:

                available_players.append(player_data)

        #
        # Determine whose turn it actually is
        #

        captain = await DraftManager.get_current_captain(
            session,
            match
        )

        current_captain = "Draft Complete"
        is_current_captain = False

        login_id = str(request.session.get("discord_id", ""))

        if captain:

            riot = await PlayerManager.get_riot_account_info(
                captain.discord_id
            )

            current_captain = (
                f"{riot['riot_name']}#{riot['riot_tag']}"
            )

            is_current_captain = (
                login_id == str(captain.discord_id)
            )

        return templates.TemplateResponse(
            request,
            "match.html",
            {

                "match": match,

                "team1": team1,

                "team2": team2,

                "available_players": available_players,

                "current_captain": current_captain,

                "logged_in": login_id,

                "authorized": login_id in discord_ids,

                "is_current_captain": is_current_captain,

                # Timer length shown on page
                "pick_time": DraftTimer.PICK_TIME

            }
        )

@app.post("/match/{match_code}/pick")
async def make_pick(match_code: str,request: PickRequest):

    async with SessionLocal() as session:

        match = await MatchManager.getMatch(
            session,
            match_code
        )

        if not match:

            return {

                "success": False,
                "error": "Match not found."

            }

        success = await DraftManager.make_pick(

            session,

            match,

            request.player_id

        )

        if not success:

            return {

                "success": False,

                "error": "Unable to draft player."

            }

        return {

            "success": True

        }



    async with SessionLocal() as session:

        match = await MatchManager.getMatch(
            session,
            match_code
        )

        if not match:
            return {
                "success": False
            }

        players = await MatchManager.get_match_players(
            session,
            match.match_id
        )

        drafted = sum(
            1
            for p in players
            if p.team is not None and not p.is_captain
        )

        captain = await DraftManager.get_current_captain(
            session,
            match
        )

        captain_id = captain.discord_id if captain else None

        remaining = DraftTimer.get_remaining(match.match_id)

        return {
            "success": True,
            "drafted": drafted,
            "captain": captain_id,
            "remaining": remaining
        }

@app.get("/match/{match_code}/draft")
async def draft_page(request: Request, match_code: str):

    

    if "discord_id" not in request.session:
            return RedirectResponse("/login")
    

    async with SessionLocal() as session:

        match = await MatchManager.getMatch(session, match_code)

        if not match:
            return RedirectResponse("/")
    
        discord_id = request.session['discord_id']
        if not await MatchManager.check_in_match(session, match.match_id, str(discord_id)):
            return RedirectResponse(f"/match/{match_code}")

        team1 = await MatchManager.get_team_players(
            session,
            match.match_id,
            team=1
        )

        team2 = await MatchManager.get_team_players(
            session,
            match.match_id,
            team=2
        )

        available_players = await MatchManager.get_available_players(
            session,
            match.match_id
        )

        return templates.TemplateResponse(
            "draft.html",
            {
                "request": request,
                "match": match,
                "team1": team1,
                "team2": team2,
                "available_players": available_players,
            }
        )

@app.get("/match/{match_code}/draft/state")
async def draft_state(match_code: str):
    
    async with SessionLocal() as session:

        match = await MatchManager.getMatch(session, match_code)
        print(f"Draft state requested for match {match_code}")
        if not match:
            return {"success": False}
        print(f"Draft state requested for match {match_code}")
        return await DraftManager.get_draft_state(
            session,
            match
        )

@app.websocket("/ws/match/{match_code}")
async def draft_socket(websocket: WebSocket, match_code: str):

    await draft_connections.connect(match_code, websocket)

    #await websocket.send_text("Hello from the server!")

    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "test":

                await draft_connections.broadcast(
                    match_code,
                    data
                )

            elif data["type"] == "pick":

                async with SessionLocal() as session:

                    match = await MatchManager.getMatch(session, match_code)
                    success = await DraftManager.make_pick(session, match, data["player_id"])

                    if success:

                        await draft_connections.broadcast(
                            match_code,
                            {
                                "type": "refresh"
                            }
                        )
                    
                #print("Player selected:", data["player_id"])

    except WebSocketDisconnect:
        draft_connections.disconnect(match_code, websocket)
        print(f"{match_code}: Disconnected")