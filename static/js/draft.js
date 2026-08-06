const socket = new WebSocket(
    `ws://${window.location.host}/ws/match/${MATCH_CODE}`
);

socket.onopen = async () => {
    console.log("Connected!");
    await loadDraftState();
};

socket.onmessage = async (event) => {
    const data = JSON.parse(event.data);
    console.log("Received refresh:", data);
    if (data.type === "refresh") {  
        await loadDraftState();
    }
};

socket.onclose = () => {
    console.log("Disconnected!");
};


let redirecting = false;
async function loadDraftState() {
    
    const response = await fetch(
        `/match/${MATCH_CODE}/draft/state`
    );

    const data = await response.json();
    console.log(data);
    console.log("Current status:", data.status);
    // Update the current pick display
    const currentPick = document.getElementById("current-pick");

    if (data.current_captain) {
        currentPick.textContent =
            `${data.current_captain.riot_name}#${data.current_captain.riot_tag}`;
    } else {
        currentPick.textContent = "Draft Complete";
    }

    // Get the Available Players container
    const container = document.getElementById("available-players");

    // Remove the old buttons
    container.innerHTML = "";

    // Add a new button for each available player
    data.available_players.forEach(player => {

        const button = document.createElement("button");

        button.className = "player draft-player";
        button.dataset.player = player.discord_id;

        button.disabled = data.current_captain.discord_id !== DISCORD_ID;

        button.innerHTML = `
            <div class="player-left">
                ${player.riot_name}#${player.riot_tag}
            </div>

            <div class="player-elo">
                ${player.elo}
            </div>
        `;

        container.appendChild(button);
        
    });
    setupPlayerButtons();
    updateTeam("team1", data.team_1_players);
    updateTeam("team2", data.team_2_players);

    if (data.status === "VOTE" || data.status === "MAP_BAN" || data.status === "SIDE") {

            document.getElementById("current-pick").textContent =
                "Draft Complete!";

            document.getElementById("draft-timer").textContent =
                "Starting Map Ban...";

            if (!redirecting) {
                redirecting = true;
                setTimeout(() => {
                    window.location.href = `/match/${MATCH_CODE}/mapban`;
                }, 5000);
            }

        return;
    } else {
        // Update the timer
        startTimer(data.remaining_timer);
    }

}

function setupPlayerButtons() {

    const playerButtons = document.querySelectorAll(".draft-player");

    playerButtons.forEach(button => {

        button.addEventListener("click", () => {
            
            console.log(`Picked player: ${button.dataset.player}`);
            socket.send(JSON.stringify({
                type: "pick",
                player_id: button.dataset.player
            }));

        });

    });

}

function updateTeam(containerId, players) {

    const container = document.getElementById(containerId);

    container.innerHTML = "";
    
    players.forEach(player => {

        const div = document.createElement("div");

        div.className = "player";

        div.innerHTML = `
            <div class="player-left">
                ${player.is_captain ? "⭐ " : ""}
                ${player.riot_name}#${player.riot_tag}
            </div>

            <div class="player-elo">
                ${player.elo}
            </div>
        `;

        container.appendChild(div);

    });

    // Fill remaining empty slots
    while (container.children.length < 5) {

        const empty = document.createElement("div");

        empty.className = "player empty";
        empty.textContent = "Empty Slot";

        container.appendChild(empty);

    }

}

let timerInterval = null;

function startTimer(seconds) {

    const timer = document.getElementById("draft-timer");

    clearInterval(timerInterval);

    timer.textContent = seconds;

    timerInterval = setInterval(() => {

        seconds--;

        timer.textContent = Math.max(0, seconds);

        if (seconds <= 0) {
            clearInterval(timerInterval);
        }

    }, 1000);

}