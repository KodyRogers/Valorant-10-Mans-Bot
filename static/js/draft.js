const socket = new WebSocket(
    `ws://${window.location.host}/ws/match/${MATCH_CODE}`
);

socket.onopen = () => {
    console.log("Connected!");
    await loadDraftState();
};

socket.onmessage = async (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "refresh") {
        await loadDraftState();
    }
};

socket.onclose = () => {
    console.log("Disconnected!");
};

async function loadDraftState() {

    const response = await fetch(
        `/match/${MATCH_CODE}/draft/state`
    );

    const data = await response.json();

    console.log(data);
}

const playerButtons = document.querySelectorAll(".draft-player");

playerButtons.forEach(button => {

    button.addEventListener("click", () => {

        console.log(button.dataset.player);

    });

});