const socket = new WebSocket(
    `ws://${window.location.host}/ws/match/${MATCH_CODE}`
);

socket.onopen = async () => {

    console.log("Connected");

    await loadBanState();

};

socket.onmessage = async (event) => {

    const data = JSON.parse(event.data);
    console.log("Received message:", data);
    if (data.type === "refresh") {
        await loadBanState();
    }

};

socket.onclose = () => {

    console.log("Disconnected");

};

async function loadBanState() {

    const response = await fetch(
        `/match/${MATCH_CODE}/mapban/state`
    );

    const data = await response.json();
    console.log("Ban state:", data);
    
    if (!data.success) {
        return;
    }

    setPhase(data.status);

    if (data.status === "VOTE") {

        updateVoteTimer(data.time_remaining);
        updateVoteCount(data.vote_count, data.total_players);

    }
    else if (data.status === "MAP_BAN") {

        updateTimer(data.time_remaining);
        updateMaps(data.banned_maps);
        updateCurrentCaptain(data.current_captain);
        updateBannedMaps(data.banned_maps);

    }
    else if (data.status === "SIDE") {

        updateTimer(data.time_remaining);

        document.getElementById("selected-map").textContent =
            data.selected_map;

    }

}

function setPhase(phase) {

    document.getElementById("vote-section").hidden = true;
    document.getElementById("ban-section").hidden = true;
    document.getElementById("side-section").hidden = true;

    const badge = document.getElementById("phase-title");
    console.log("Setting phase to:", phase);
    switch (phase) {

        case "VOTE":

            document.getElementById("vote-section").hidden = false;

            badge.textContent = "Map Pool Vote";
            badge.className = "match-status voting";

            break;

        case "MAP_BAN":

            document.getElementById("ban-section").hidden = false;

            badge.textContent = "Map Ban";
            badge.className = "match-status banning";

            break;

        case "SIDE":

            document.getElementById("side-section").hidden = false;

            badge.textContent = "Choose Side";
            badge.className = "match-status side-select";

            break;

    }

}

function updateMaps(bannedMaps) {

    document.querySelectorAll(".map-card").forEach(card => {

        const mapName = card.dataset.map;

        if (bannedMaps.includes(mapName)) {

            card.classList.add("banned");
            card.disabled = true;

        } else {

            card.classList.remove("banned");
            card.disabled = false;

        }

    });

}

function updateCurrentCaptain(captain) {

    document.getElementById("current-ban").textContent = captain;

}

function updateTimer(seconds) {

    document.getElementById("ban-timer").textContent = seconds;

}

function updateBannedMaps(bannedMaps) {

    const container = document.getElementById("banned-maps");

    if (bannedMaps.length === 0) {

        container.textContent = "None";

        return;

    }

    container.textContent = bannedMaps.join(", ");

}

/* ========================================= */
/* MAP BANS */
/* ========================================= */

document.querySelectorAll(".map-card").forEach(card => {

    card.addEventListener("click", () => {

        if (card.classList.contains("banned")) {
            return;
        }

        socket.send(JSON.stringify({

            type: "ban_map",
            map: card.dataset.map

        }));

    });

});

/* ========================================= */
/* MAP POOL VOTE */
/* ========================================= */

document.querySelectorAll(".pool-button").forEach(button => {

    button.addEventListener("click", () => {

        document.querySelectorAll(".pool-button").forEach(btn => {
            btn.classList.remove("selected");
        });

        button.classList.add("selected");

        socket.send(JSON.stringify({

            type: "vote_pool",
            pool: button.dataset.pool

        }));

    });

});

/* ========================================= */
/* SIDE SELECT */
/* ========================================= */

document.querySelectorAll(".side-button").forEach(button => {

    button.addEventListener("click", () => {

        socket.send(JSON.stringify({

            type: "pick_side",
            side: button.dataset.side

        }));

    });

});


/* ========================================= */
/* VOTE TIMER */
/* ========================================= */
function updateVoteTimer(seconds) {

    document.getElementById("vote-timer").textContent = seconds;

}

function updateVoteCount(votes, totalPlayers) {

    document.getElementById("vote-count").textContent =
        `${votes} / ${totalPlayers}`;

}