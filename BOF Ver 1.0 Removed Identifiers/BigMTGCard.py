import discord

class BigMTGCard(discord.ui.Modal):
    def __init__(self, client, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.client = client
        self.iscallback = False
        self.add_item(discord.ui.InputText(label="Name of the card you want."))
        self.add_item(discord.ui.InputText(label="Card details.", style=discord.InputTextStyle.long, max_length = 800, placeholder= "Mana cost, abilities, power/toughness, creature type..."))
        self.add_item(discord.ui.InputText(label="Flavor text and any aditional info", style=discord.InputTextStyle.long, max_length = 800,))

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Big One MTG Card Request")
        embed.add_field(name="Name of the card you want.", value=self.children[0].value)
        embed.add_field(name="Mana cost, abilities, power/toughness, creature type...", value=self.children[1].value)
        embed.add_field(name="Flavor text and any aditional info", value=self.children[2].value)
        await interaction.response.send_message(embeds=[embed])
        embed.add_field(name="person who sent request", value=interaction.user.display_name)
        big = self.client.get_user(251385361412915201)
        await big.send(embeds=[embed])
        
        self.iscallback = True