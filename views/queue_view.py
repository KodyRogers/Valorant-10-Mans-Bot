import discord

from managers.queue_manager import QueueManager
from managers.player_manager import PlayerManager

class QueueView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    # ===================================
    # EMBED
    # ===================================

    @staticmethod
    async def build_embed(queue):

        embed = discord.Embed(
            title="🏆 Kodhi's 10 Man Queue",
            color=discord.Color.red()
        )

        if len(queue) == 0:
            players = "No players currently in queue."
        else:
            players = ""

            for index, player in enumerate(queue, start=1):
                riot_info = await PlayerManager.get_riot_account_info(player.discord_id)
                mrr = await PlayerManager.get_player_mmr(player.discord_id)
                riot_id = f"{riot_info['riot_name']}#{riot_info['riot_tag']}" if riot_info else "Unknown"
                players += f"**{index}.** <@{player.discord_id}> ({riot_id}) - MMR: {mrr}\n"

        embed.add_field(
            name="Players",
            value=players,
            inline=False
        )

        embed.add_field(
            name="Queue",
            value=f"{len(queue)}/10 Players",
            inline=False
        )

        remaining = 10 - len(queue)

        if remaining == 0:
            status = "Starting draft..."
        elif remaining == 1:
            status = "Waiting for 1 more player."
        else:
            status = f"Waiting for {remaining} more players."

        embed.add_field(
            name="Status",
            value=status,
            inline=False
        )

        embed.set_footer(
            text="Use the buttons below to join or leave the queue."
        )

        return embed

    # ===================================
    # JOIN
    # ===================================

    @discord.ui.button(
        label="Join Queue",
        style=discord.ButtonStyle.success,
        emoji="✅"
    )
    async def join(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        success, message, queue_size = await QueueManager.join_queue(
            str(interaction.user.id)
        )

        if not success:
            await interaction.response.send_message(
                message,
                ephemeral=True
            )
            return

        queue = await QueueManager.get_queue()

        await interaction.message.edit(
            embed=await self.build_embed(queue),
            view=self
        )

        await interaction.response.send_message(
            message,
            ephemeral=True
        )

        if queue_size >= 10:
            pass
            #players = await QueueManager.pop_first_ten()

            #await MatchManager.create_match (
            #    interaction = interaction,
            #    players = players
            #)

    # ===================================
    # LEAVE
    # ===================================

    @discord.ui.button(
        label="Leave Queue",
        style=discord.ButtonStyle.danger,
        emoji="❌"
    )
    async def leave(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        success, message, queue_size = await QueueManager.leave_queue(
            str(interaction.user.id)
        )

        if not success:
            await interaction.response.send_message(
                message,
                ephemeral=True
            )
            return

        queue = await QueueManager.get_queue()

        await interaction.message.edit(
            embed=await self.build_embed(queue),
            view=self
        )

        await interaction.response.send_message(
            message,
            ephemeral=True
        )