from re import match

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from httpcore import request
from sqlalchemy import select

from starlette.middleware.sessions import SessionMiddleware

from config import SESSION_SECRET

from database import SessionLocal
from managers.map_ban_manager import MapBanManager
from managers.match_manager import MatchManager
from managers.player_manager import PlayerManager
from managers.draft_manager import DraftManager
from managers.draft_timer import DraftTimer
from managers.websocket_manager import draft_connections
from managers.map_ban_timer import MapTimer

from models import Player
from routes.pick_request import PickRequest
from routes.login import router

import time
import requests

app = FastAPI()


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
        
        team1 = []
        team2 = []

        for player in match_players:

            riot = await PlayerManager.get_riot_account_info(player.discord_id)
            elo = await PlayerManager.get_player_mmr(player.discord_id)

            if not riot:
                continue

            player_data = {

                "discord_id": player.discord_id,

                "riot_name": riot["riot_name"],
                "riot_tag": riot["riot_tag"],

                "elo": elo,

                "team": player.team,

                "is_captain": player.is_captain

            }

            if player.team == 1:
                team1.append(player_data)

            elif player.team == 2:
                team2.append(player_data)

           
        # if "discord_id" not in request.session:
        #     request.session["next_url"] = str(request.url.path)
        #     print(f"User not logged in, redirecting to login. Next URL: {request.session['next_url']}")
        #     return RedirectResponse("/login")
        # discord_id = str(request.session.get("discord_id", ""))
        # if await MatchManager.check_in_match(session, match.match_id, str(discord_id)):
    
        #     if match.status == "DRAFTING":
        #         return RedirectResponse(f"/match/{match_code}/draft")
        #     elif match.status == "VOTE" or match.status == "MAP_BAN" or match.status == "SIDE":
        #         return RedirectResponse(f"/match/{match_code}/mapban")
        #     elif match.status == "LIVE":
        #         return RedirectResponse(f"/match/{match_code}/live")
        # else:
        #     print(f"User {discord_id} is not in match {match_code}, redirecting to login")
        #     #return RedirectResponse("/login")

        return templates.TemplateResponse(
            request,
            "match.html",
            {
                "match": match,
                "team1": team1,
                "team2": team2,

            }
        )

@app.get("/match/{match_code}/draft")
async def draft_page(request: Request, match_code: str):

    async with SessionLocal() as session:

        match = await MatchManager.getMatch(session, match_code)
        if not match:
            return RedirectResponse("/")   

        # Check if the user is in the match
        if "discord_id" not in request.session:
            request.session["next_url"] = str(request.url.path)
            print(f"User not logged in, redirecting to login. Next URL: {request.session['next_url']}")
            return RedirectResponse("/login")

        # Check if the user is in the match
        discord_id = str(request.session.get("discord_id", ""))
        if not await MatchManager.check_in_match(session, match.match_id, str(discord_id)):
    
            if match.status == "DRAFTING":
                return RedirectResponse(f"/match/{match_code}/draft")
            elif match.status == "VOTE" or match.status == "MAP_BAN" or match.status == "SIDE":
                return RedirectResponse(f"/match/{match_code}/mapban")
            elif match.status == "LIVE":
                return RedirectResponse(f"/match/{match_code}/live")
        else:
            print(f"User {discord_id} is not in match {match_code}, redirecting to login")

        return templates.TemplateResponse(
            "draft.html",
            {
                "request": request,
                "match": match
            }
        )

@app.get("/match/{match_code}/mapban")
async def map_ban_page(request: Request, match_code: str):

    async with SessionLocal() as session:

        match = await MatchManager.getMatch(session, match_code)

        if not match:
            return RedirectResponse("/")

        return templates.TemplateResponse(
            "map_ban.html",
            {
                "request": request,
                "match": match
            }
        )

@app.get("/match/{match_code}/live")
async def live_match_page(request: Request, match_code: str):

    async with SessionLocal() as session:

        match = await MatchManager.getMatch(session, match_code)

        if not match:
            return RedirectResponse("/")

        return templates.TemplateResponse(
            "live.html",
            {
                "request": request,
                "match": match
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

@app.get("/match/{match_code}/mapban/state")
async def map_ban_state(match_code: str):
    async with SessionLocal() as session:

        match = await MatchManager.getMatch(session, match_code)
        
        if not match:
            return {"success": False} 
        
        return await MapBanManager.get_map_ban_state(
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
                    success = await DraftManager.make_pick(session, match, websocket.session["discord_id"], data["player_id"])

                    if success:

                        await DraftTimer.start(match.match_id)
                        
                        await draft_connections.broadcast(
                            match_code,
                            {
                                "type": "refresh"
                            }
                        )

            elif data["type"] == "vote_pool":
                async with SessionLocal() as session:

                    match = await MatchManager.getMatch(session, match_code)

                    if not match:
                        await websocket.send_json({
                            "success": False,
                            "error": "Match not found."
                        })
                        continue

                    await MapBanManager.vote(
                        session,
                        match,
                        websocket.session["discord_id"],
                        data['pool']
                    )

                    
                    await draft_connections.broadcast(
                        match_code,
                        {
                            "type": "refresh"
                        }
                    )
                    
            elif data["type"] == "ban_map":
                async with SessionLocal() as session:
                    match = await MatchManager.getMatch(session, match_code)
                    if not match:
                        await websocket.send_json({
                            "success": False,
                            "error": "Match not Found."
                        })
                        continue
            
                    success = await MapBanManager.ban_map(session, match, str(websocket.session["discord_id"]), str(data['map']))
                    if success:
                        await MapTimer.start(match.match_id)
                        await draft_connections.broadcast(
                            match_code, {"type": "refresh"}
                        )

            elif data["type"] == "pick_side":
                async with SessionLocal() as session:
                    match = await MatchManager.getMatch(session, match_code)
                    if not match:
                        await websocket.send_json({
                            "success": False,
                            "error": "Match not Found."
                        })
                        continue
                    success = await MapBanManager.choose_side(session, match, str(websocket.session["discord_id"]), str(data["side"]))
                    if success:
                        await draft_connections.broadcast(
                            match_code, {"type": "refresh"}
                        )

            print("else:", data)

    except WebSocketDisconnect:
        draft_connections.disconnect(match_code, websocket)
        print(f"{match_code}: Disconnected")