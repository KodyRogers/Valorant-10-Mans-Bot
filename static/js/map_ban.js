const socket = new WebSocket(
    `ws://${window.location.host}/ws/match/${MATCH_CODE}`
);

socket.onopen = async () => {

    console.log("Connected");

    await loadBanState();

};

socket.onmessage = async (event) => {

    const data = JSON.parse(event.data);

    if (data.type === "refresh") {
        await loadBanState();
    }

};

socket.onclose = () => {

    console.log("Disconnected");

};

async function loadBanState() {

    const response = await fetch(
        `/match/${MATCH_CODE}/ban/status`
    );

    const data = await response.json();

    if (!data.success) {
        return;
    }

    updateMaps(data.banned_maps);

    updateCurrentCaptain(data.current_captain);

    updateTimer(data.time_remaining);

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