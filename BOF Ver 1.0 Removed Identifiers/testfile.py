from discord import Intents
from discord.ext import commands
from discord import ui, Interaction, SelectOption, Message, ButtonStyle

class Dropdown(ui.Select):
    def __init__(self):
        options=[
            SelectOption(label="Option 1", value="1"),
            SelectOption(label="Option 2", value="2"),
            SelectOption(label="Option 3", value="3"),
        ]
        super().__init__(placeholder="Select an option", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction):
        self.view.value = self.values[0]
        await interaction.response.send_message(f"Selected: {self.values[0]}", ephemeral=True)

class MyView(ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.add_item(Dropdown())
        self.add_item(ui.Button(label="Submit your text", style=ButtonStyle.primary, custom_id="submit"))

    @ui.button(label="Submit your text", style=ButtonStyle.primary, custom_id="submit")
    async def submit(self, button: ui.Button, interaction: Interaction):
        await interaction.response.send_message("Please reply to this message with your text.", ephemeral=True)

        def check(m: Message):
            return m.author == interaction.user and m.reference and \
                   m.reference.resolved.to_reference().message_id == interaction.message.id

        message = await self.wait_for('message', check=check)
        await interaction.followup.send(f"You wrote: {message.content}")

class Bot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)

        self.add_view(MyView())

    @commands.command()
    async def amog(self, ctx):
        await ctx.send("Here's your dialog", view=MyView())

bot = Bot()
bot.add_command(bot.amog)
bot.run("MTA1MzI1NDQ4NzQ3ODkxMTAyNg.G-y-w0.3Bh_Zux_EjCw7cjUs1tNu7T2xNH6IkozQnzAIE")
