import json
import os
import random
import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

zapi = "https://zenquotes.io/api/"

# Botón personalizado para el juego
class RPSButton(discord.ui.Button):
    def __init__(self, label, style, player: discord.User):
        super().__init__(label=label, style=style, custom_id=label)

    async def callback(self, interaction: discord.Interaction):
        # Check if it's the user's turn
        if interaction.user != self.view.player:
            await interaction.response.send_message("¡No es tu turno!", ephemeral=True)
            return

        # saving choice
        self.view.user_choices[self.view.player.id] = self.custom_id
        self.view.player = self.view.challenger

        # check results
        if len(self.view.user_choices) == 2:
            sender_choice = self.view.user_choices[self.view.challenger.id]
            target_choice = self.view.user_choices[self.view.challenged.id]

            if sender_choice == target_choice:
                await interaction.response.send_message(f"It's a draw!, both players chose {sender_choice}.")
            elif user_wins(target_choice, sender_choice):
                await interaction.response.send_message(
                    f"{self.view.challenger.mention} has won using {sender_choice} against {target_choice}!")
            else:
                await interaction.response.send_message(
                    f"{self.view.challenged.mention} has won using {target_choice} against {sender_choice}!")

            self.view.stop()

        # Si solo un jugador ha elegido, avisamos que es el turno del otro jugador
        else:
            await interaction.response.send_message(f"Now it's {self.view.challenger.mention}'s turn!")

class RPSView(discord.ui.View):
    def __init__(self, challenged: discord.User, challenger: discord.User):
        super().__init__()

        self.challenged = challenged
        self.challenger = challenger
        self.player = challenged
        self.user_choices = {}

        # buttons
        self.add_item(RPSButton(label='rock', style=discord.ButtonStyle.green, player=challenged))
        self.add_item(RPSButton(label='paper', style=discord.ButtonStyle.blurple, player=challenged))
        self.add_item(RPSButton(label='scissors', style=discord.ButtonStyle.red, player=challenged))
@bot.command(name="solo", help="Play a game of rock paper scissors with the bot!")
async def rock_paper_scissors(ctx, user_choice, *, arg: str = "None"):
    rps = ["rock", "paper", "scissors"]
    bot_choice = random.choice(rps)
    user_choice = user_choice.lower()
    if user_choice == bot_choice:
        await ctx.send(f"We both picked **{bot_choice}**. We tied...")
    elif bot_wins(bot_choice, user_choice):
        await ctx.send(f"I won! I chose **{bot_choice}** and you picked **{user_choice}**. This proves I'm superior.")
    elif user_wins(bot_choice, user_choice):
        await ctx.send(f"What!? I chose **{bot_choice}** and you picked **{user_choice}**. You win and now I'm sad :(")
    else: await ctx.send(f"You need to pick either **{rps[0]}**, **{rps[1]}** or **{rps[2]}** to play!")

@rock_paper_scissors.error
async def rock_paper_scissors_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Provide your choice along with the command!")

def bot_wins(bc:str, uc:str):
    if (uc == "rock" and bc == "paper") or (uc == "paper" and bc == "scissors") or (uc == "scissors" and bc == "rock"):
        return True
    else:
        return False

def user_wins(bc:str, uc:str):
    if (uc == "rock" and bc == "scissors") or (uc == "paper" and bc == "rock") or (uc == "scissors" and bc == "paper"):
        return True
    else:
        return False

@bot.command(name="play", help="Challenge someone to a game of rock paper scissors!")
async def play(ctx, target: discord.User,):
    choices = ["rock", "paper", "scissors"]
    sender = ctx.message.author
    if sender == target:
        await ctx.send("You can't play against yourself!")
        return
    elif target.bot:
        await ctx.send("You can't play with bots!")
        return

    embed = discord.Embed(title="Rock - Paper - Scissors", description=f"It's {target}'s turn!", color=discord.Color.dark_embed(), timestamp=ctx.message.created_at)

    view = RPSView(target, sender)

    await ctx.send(content=f"{target.mention}, you have been challenged by {sender.mention} to a Rock Paper Scissors Match! "
                           f"To start playing, click one of the buttons below.", embed=embed, view=view)

@bot.command(name="zen", help="Get a random zen quote")
async def zen(ctx):
    res = requests.get(zapi+"random")
    data = json.loads(json.dumps(res.json()[0]))
    quote = data["q"]
    author = data["a"]
    await ctx.send(f"*{quote}*  -**{author}**")

@bot.command(name="qod", help="Get the zen quote of the day")
async def qod(ctx):
    res = requests.get(zapi+"today")
    data = json.loads(json.dumps(res.json()[0]))
    quote = data["q"]
    author = data["a"]
    await ctx.send(f"*{quote}*  -**{author}**")

bot.run(TOKEN)