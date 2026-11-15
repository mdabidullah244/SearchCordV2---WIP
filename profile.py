from cache import profile_cache
import random
import psycopg
import discord
from discord import app_commands
from discord.ext import commands
#all of the work that is being done with 'PostgreSQL' is done within the 'profile_cache.py' directory

#the logic behind this entire cog will be
#if the user has a profile
    #send an embed with their info
#if the user does not have a profile
    #send an embed asking if they want to create one
    #if they click yes
        #send a modal asking for their username, bio, and bias (all optional, all have defaults)
        #send them an embed with their newly created profile
    #if they click no
        #send an embed reassuring them that no profile has been created

username_placeholders = [
    "What's your username gonna be?",
    "Enter something wimpus would love!",
    "Go on, enter your username!"
]
biography_placeholders = [
    "Anything interesting gonig on?",
    "What're you most excited for?",
    "Maybe your birthday?",
    "Something you love... or hate"
]
bias_placeholders = [
    "Who's your fav character?", 
    'Who do you look up to the most?',
    'Put someone cool!'
]
footer_text = [
    "Use '/help' if you're curious about something!⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "Want to search up your favorite anime? Use '/search'⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "Check out someone's profile using '/view'!⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ "
]

def embed_gen(title: str, author_icon_urL: str, footer_text: str):
    embed = discord.Embed(color = discord.Color.from_str('#FFFFFF'))
    embed.set_author(name = title, icon_url = author_icon_urL)
    embed.set_footer(text = footer_text)
    return embed

#the modal doesn't need a 'def __init()' but you could put one if you wanted to
#we define each of the categories we want from the user using 'discord.ui.Label(...)'
#inside of 'discord.ui.Label(...)' are 'text' and 'component'.
#'text' is what is above the text input
#'component' is somewhat arleady in the name itself, think of it as 'what component will add functionality to my button'
#here that's 'discord.ui.TextInput(...)' because we want the user to input information into the modal
#and insice of 'discord.ui.TextInput(...)', theres various amounts of pararmeters but the most important ones
#are argubaly 'label' which should give a quick descrption of what this input box is about
#'style' which changes the style of the input box (to hold big/small amount of chars)
#and 'required' which is if the input box is optional or not

#also notice how we are adding functionality to UI, hence why we're using 'discord.ui'
class profileModal(discord.ui.Modal, title = 'Profile | Creation'):
    username = discord.ui.Label(
        text = 'Username',
        component = discord.ui.TextInput(placeholder=random.choice(username_placeholders), required=False)
    )
    biography = discord.ui.Label(
        text = 'Bio',
        component = discord.ui.TextInput(placeholder=random.choice(biography_placeholders), style = discord.TextStyle.paragraph, required = False)
    )
    bias = discord.ui.Label(
        text = 'Bias',
        component = discord.ui.TextInput(placeholder=random.choice(bias_placeholders), required = False)
    )

    async def on_submit(self, interaction: discord.Interaction):
        username = interaction.user.name if self.username.component.value.strip() == '' else self.username.component.value.strip()
        biography = 'Nothing to see here yet...' if self.biography.component.value.strip() == '' else self.biography.component.value.strip()
        bias = 'Nope, nothing here too!' if self.bias.component.value.strip() == '' else self.bias.component.value.strip()

        try:
            await profile_cache.create_profile(interaction.user.id, username, biography, bias)
            embed = embed_gen('Profie | Creation Successful', interaction.user.avatar, random.choice(footer_text))
            embed.set_thumbnail(url = interaction.user.avatar)
            embed.add_field(name = 'Username', value = username, inline=False)
            embed.add_field(name = 'Bio', value = biography, inline=False)
            embed.add_field(name = 'Bias', value = bias, inline=False)
            await interaction.response.edit_message(embed = embed, view = None)
        except psycopg.Error as error: # ERROR
            print(f'\nCREATE PROFILE postgresql ERROR: {error}\n')
            embed = embed_gen('Profile | Creation Error', interaction.user.avatar, 'Fixing things up...')
            embed.add_field(name = 'ERROR', value = "Something went wrong when we tried to create your profile")
            await interaction.response.edit_message(embed = embed)
#we need to create a seperate class for each button
#this is because each class will hold functionality for each button object it creates
class yesButton(discord.ui.Button):
    #for the intializer, instead of configuring the entire thing (since the parameters for the initailizer are huge)
    #we can simply just call the parent intailzier and make changes to our own intializer 
    # so we don't have to worry about the huge amount of parameters
    def __init__(self):
        super().__init__(
            label = '✓',
            style = discord.ButtonStyle.green
        )

    #at this point we already made our button (yes its that simple), now we add functionality to it
    async def callback(self, interaction: discord.Interaction):
        #notice how we don't need a view for a modal because its esseitnaly like a pop up, there's a seperate way to send modals
        #also check if the original user clicked on the button
        await interaction.response.send_modal(profileModal())

class noButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label = '✗',
            style = discord.ButtonStyle.red
        )

    async def callback(self, interaction: discord.Interaction):
        embed = embed_gen('Profile | Creation Cancled', interaction.user.avatar, random.choice(footer_text))
        await interaction.response.edit_message(embed=embed, view=None)


#the 'view' will mnost likely control if i were to send buttons vs modals depending on the circumstance
class profileView(discord.ui.View):
    def __init__(self, user_id: int):
        #we need to add 'super().__init__()' because we override the original 'discord.ui.View' intializer
        #that intializer creates the '_children' attribute which lets us use 'self.add_items(...)'
        #which esseitnaly means that the 'yesButton()' and 'noButton' are the children of 'discord.ui.View' 
        super().__init__()
        self.user_id = user_id
        #we're adding an instance (object) of each button, NOT the class itself.
        #which is why we do 'yesButton()' and 'noButton()' instead of 'yesButton' and 'noButton'
        self.add_item(yesButton())
        self.add_item(noButton())

    #we don't need to pass the 'user_id' into other classes such as the 'yesButton' and 'noButton' classes
    #instead since those classes/'buttons'/'containers' are managed by 'view' itself
    #we can use 'async def interaction_check(...) to see if the original user is interacting with the 'view'
    #this idea is also similar to that of how 'async def on_timeout(self)' works!
    #we don't use an independent timer within the 'yesButton' and 'noButton' classes
    #isntead we use the 'view' which literly maintains them 
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            embed = embed_gen('Profile | This Is Not Your Command', interaction.user.avatar, random.choice(footer_text))
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

class profileCog(commands.Cog):
    def __init__(self):
        super().__init__()

    @app_commands.command(name = 'profile', description = 'View your own profile or create a new one')
    @app_commands.checks.cooldown(1, 5.0, key = lambda interaction: (interaction.user.id))
    async def profile(self, interaction: discord.Interaction):
        #the user uses this command, check if they have a profile
        #if they dont then send them a modal which asks for their information
        #if the user already has a profile then send them their information
        try:
            userinfo = await profile_cache.get_profile(interaction.user.id)
            if userinfo is None:
                embed = embed_gen("Profile | Uh oh! Look's like you have no profile!", interaction.user.avatar, random.choice(footer_text))
                await interaction.response.send_message(embed = embed, view = profileView(interaction.user.id))
                return
            
            embed = embed_gen(userinfo[0], interaction.user.avatar, random.choice(footer_text))
            embed.set_thumbnail(url=interaction.user.avatar)
            embed.add_field(name='Bias', value=userinfo[2], inline=False)
            embed.add_field(name='Bio', value=userinfo[1], inline=False)
            await interaction.response.send_message(embed=embed)
        except psycopg.Error as error: # ERROR
            print(f'\nGET PROFILE postgresql ERROR: {error}\n')
            embed = embed_gen('Profile | Creation Error', interaction.user.avatar, 'Fixing things up...')
            embed.add_field(name = 'ERROR', value = 'Something went wrong when we tried to get your profile')
            await interaction.response.send_message(embed = embed, ephemeral=True)

    @profile.error # ERROR
    async def on_help_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = embed_gen('Profile | Cooldown', interaction.user.avatar, f'Retry after: {int(error.retry_after)} seconds')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        print(f'\nPROFILE command ERROR: {error}\n')
        embed = embed_gen('Profile | Unkonwn Error', interaction.user.avatar, 'Fixing things up...')
        await interaction.response.send_message(embed=embed, ephemeral=True)

    #make sure to impliment command cooldowns, a cooldown error would happen and then we would need an error handeler
    #that makes sure that the error that occured is an instance of cooldown and then responds to it
    #by sending an embed with the error message and how long until the user can send the command again

        

async def setup(bot):
    #notice we can't just pass the class into "bot.add_cog(...)"
    #we would need an instance of the class itself
    await bot.add_cog(profileCog())