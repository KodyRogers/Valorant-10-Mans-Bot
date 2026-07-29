document.addEventListener("DOMContentLoaded", () => {

    const cards = document.querySelectorAll(".selectable");

    const timer = document.getElementById("draft-timer");

    let seconds = Number(timer.textContent);

    setInterval(() => {

        if (seconds <= 0)
            return;

        seconds--;

        timer.textContent = seconds;

    }, 1000);

    // Disable all buttons if this user isn't the current captain
    if (!CAN_PICK) {

        cards.forEach(card => {

            card.disabled = true;
            card.style.cursor = "not-allowed";
            card.title = "It isn't your turn.";

        });

        return;

    }

    cards.forEach(card => {

        card.addEventListener("click", async () => {

            // Prevent double-clicks
            cards.forEach(c => c.disabled = true);

            const playerId = Number(card.dataset.player);

            try {

                const response = await fetch(
                    `/match/${MATCH_CODE}/pick`,
                    {

                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({

                            player_id: playerId

                        })

                    }
                );

                if (!response.ok) {

                    throw new Error(
                        `HTTP ${response.status}`
                    );

                }

                const result = await response.json();

                if (!result.success) {

                    alert(result.error);

                    cards.forEach(c => c.disabled = false);

                    return;

                }

                // Refresh to show updated teams
                location.reload();

            }
            catch (err) {

                console.error(err);

                alert("An error occurred while drafting.");

                cards.forEach(c => c.disabled = false);

            }

        });

    });

});

let drafted = document.querySelectorAll(".player-card").length;

setInterval(async () => {

    const response = await fetch(
        `/match/${MATCH_CODE}/status`
    );

    const state = await response.json();

    document.getElementById("draft-timer").textContent =
        state.remaining;
    
    if (state.drafted !== drafted) {

        location.reload();

    }

}, 3000);