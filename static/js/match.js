document.addEventListener("DOMContentLoaded", () => {

    const cards = document.querySelectorAll(".selectable");
    const timer = document.getElementById("draft-timer");

    // Number of drafted players currently on the page
    let drafted = document.querySelectorAll(".player-card").length;

    // ==========================
    // Poll Server Status
    // ==========================

    async function updateStatus() {

        try {

            const response = await fetch(
                `/match/${MATCH_CODE}/status`,
                {
                    cache: "no-store"
                }
            );

            if (!response.ok)
                return;

            const state = await response.json();

            // Update timer from server
            timer.textContent = state.remaining;

            // Reload page if draft changed
            if (state.drafted !== drafted) {

                console.log("Draft updated. Reloading...");

                location.reload();

                return;

            }

        }
        catch (err) {

            console.error("Status update failed:", err);

        }

    }

    // Initial update
    updateStatus();

    // Poll every second
    setInterval(updateStatus, 1000);

    // ==========================
    // Disable buttons if not captain
    // ==========================

    if (!CAN_PICK) {

        cards.forEach(card => {

            card.disabled = true;
            card.style.cursor = "not-allowed";
            card.title = "It isn't your turn.";

        });

        return;

    }

    // ==========================
    // Pick Handler
    // ==========================

    cards.forEach(card => {

        card.addEventListener("click", async () => {

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

                    throw new Error(`HTTP ${response.status}`);

                }

                const result = await response.json();

                if (!result.success) {

                    alert(result.error);

                    cards.forEach(c => c.disabled = false);

                    return;

                }

                // Refresh immediately after a successful pick
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