
import discord

class BigSong(discord.ui.Modal):
    def __init__(self, client, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.client = client
        self.iscallback = False
        self.add_item(discord.ui.InputText(label="Name of the song you want."))
        self.add_item(discord.ui.InputText(label="Additional details.", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Big One song request")
        embed.add_field(name="Name of the song you want.", value=self.children[0].value)
        embed.add_field(name="Additional details.", value=self.children[1].value)
        await interaction.response.send_message(embeds=[embed])
        embed.add_field(name="person who sent request", value=interaction.user.display_name)
        big = self.client.get_user(251385361412915201)
        await big.send(embeds=[embed])

        self.iscallback = True