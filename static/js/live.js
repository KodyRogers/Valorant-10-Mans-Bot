const socket = new WebSocket(
    `ws://${window.location.host}/ws/match/${MATCH_CODE}`
);

socket.onopen = async () => {

    console.log("Connected");
    await loadLiveState();
};

socket.onmessage = async (event) => {

    const data = JSON.parse(event.data);

    console.log("Received:", data);

    switch (data.type) {

        case "refresh":

            await loadLiveState();
            break;

        case "match_finished":

            window.location.href =
                `/match/${MATCH_CODE}`;
            break;

    }

};

socket.onclose = () => {

    console.log("Disconnected");

};


/* ========================================= */
/* LOAD LIVE STATE */
/* ========================================= */

async function loadLiveState() {

    const response = await fetch(
        `/match/${MATCH_CODE}/live/state`
    );

    const data = await response.json();
    console.log(data)
    if (!data.success) {
        return;
    }

    if (data.status === "FINISHED") {

        window.location.href =
            `/match/${MATCH_CODE}`;

        return;

    }

}


/* ========================================= */
/* REPORT MATCH */
/* ========================================= */

document.getElementById("report-button")
    .addEventListener("click", reportMatch);


async function reportMatch() {

    const button =
        document.getElementById("report-button");

    const status =
        document.getElementById("verification-status");

    button.disabled = true;
    button.textContent = "Checking...";

    status.className = "verification checking";
    status.textContent = "Checking Riot API...";

    try {

        const response = await fetch(
            `/match/${MATCH_CODE}/report`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (data.success) {

            status.className = "verification success";
            status.textContent = "✔ Match Verified";

            button.textContent = "Reported";

        }
        else {

            status.className = "verification waiting";
            status.textContent =
                data.message || "Match not found yet.";

            button.disabled = false;
            button.textContent = "Report Match Result";

        }

    }
    catch (error) {

        console.error(error);

        status.className = "verification waiting";
        status.textContent = "Failed to contact server.";

        button.disabled = false;
        button.textContent = "Report Match Result";

    }

}