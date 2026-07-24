import random

import discord


class DraftManager:

    @staticmethod
    async def start_draft(bot, channel, players):

        # --------------------------------
        # Pick Captains
        # --------------------------------

        captains = random.sample(players, 2)

        captain1 = captains[0]
        captain2 = captains[1]

        team1 = [captain1]
        team2 = [captain2]

        # Everyone else
        pool = [
            player
            for player in players
            if player not in captains
        ]

        await channel.send(
            f"🏆 **Captains**\n"
            f"Team 1: <@{captain1.discord_id}>\n"
            f"Team 2: <@{captain2.discord_id}>"
        )

        draft_order = [
            captain1,
            captain2,
            captain2,
            captain1,
            captain1,
            captain2,
            captain2,
            captain1
        ]

        # --------------------------------
        # Draft
        # --------------------------------

        for picker in draft_order:

            available = "\n".join(
                f"- <@{p.discord_id}>"
                for p in pool
            )

            await channel.send(
                f"<@{picker.discord_id}> pick a player.\n\n"
                f"Available:\n{available}"
            )

            def check(message):

                if message.author.id != int(picker.discord_id):
                    return False

                if not message.mentions:
                    return False

                picked = str(message.mentions[0].id)

                return any(
                    p.discord_id == picked
                    for p in pool
                )

            msg = await bot.wait_for(
                "message",
                check=check
            )

            picked_id = str(msg.mentions[0].id)

            picked = next(
                p
                for p in pool
                if p.discord_id == picked_id
            )

            if picker == captain1:
                team1.append(picked)
            else:
                team2.append(picked)

            pool.remove(picked)

            await channel.send(
                f"✅ <@{picked.discord_id}> drafted."
            )

        # --------------------------------
        # Final Teams
        # --------------------------------

        team1_text = "\n".join(
            f"<@{p.discord_id}>"
            for p in team1
        )

        team2_text = "\n".join(
            f"<@{p.discord_id}>"
            for p in team2
        )

        embed = discord.Embed(
            title="Draft Complete",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Team 1",
            value=team1_text,
            inline=True
        )

        embed.add_field(
            name="Team 2",
            value=team2_text,
            inline=True
        )

        await channel.send(embed=embed)

        # TODO
        # MatchManager.create_match(team1, team2)