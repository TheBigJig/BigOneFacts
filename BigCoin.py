
import discord

class BigCoin(discord.ui.Modal):
    def __init__(self, client, coins, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.client = client
        self.coins = coins
        self.amount = 0

        self.add_item(discord.ui.InputText(label="How much BigCoin do you want to trade?", placeholder = "enter only integers EX: 1, 37 not $1, hi"))

    async def callback(self, interaction: discord.Interaction):
        try:
            self.amount = int(self.children[0].value)
            print(self.amount)

        except:
            await interaction.response.send_message("Your value was not an integer.")
            return
        
        print(self.coins)
        if self.amount > self.coins:
            await interaction.response.send_message("Your value was more than the amount of coins you have.")
            return
        
        if self.amount <= 0:
            await interaction.response.send_message("Your value was less than or equal to zero.")
            return 
        

        
        embed = discord.Embed(title="BigCoin Exchange")
        embed.add_field(name="BigCoin to USD conversion", value=self.children[0].value + " BigCoin -> $" + self.children[0].value)
        await interaction.response.send_message(embeds=[embed])
        embed.add_field(name="person who sent request", value=interaction.user.display_name)
        big = self.client.get_user(251385361412915201)
        await big.send(embeds=[embed])
