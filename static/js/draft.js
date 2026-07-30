const socket = new WebSocket(
    `ws://${window.location.host}/ws/match/${MATCH_CODE}`
);

socket.onopen = () => {
    console.log("Connected!");

    socket.send(JSON.stringify({
        type: "pick",
        player_id: "2"
    }));

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