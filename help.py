import random
import discord
from discord import app_commands
from discord.ext import commands

footer_text = [
    "Use '/help' if you're curious about something!⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "Want to search up your favorite anime? Use '/search'⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "Check out someone's profile using '/view'!⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ "
]


#embed here is an object of the class discord.Embed
def embed_gen(title: str, author_icon_url: str, footer_text: str):
    embed = discord.Embed(color = discord.Color.from_str('#FFFFFF'))
    embed.set_author(name = title, icon_url = author_icon_url)
    embed.set_footer(text = footer_text)
    return embed

#"discord.ui.Select", it differs from "discord.ui.View" as "discord.ui.Select" is the component we add functionality to
#we then add the class "helpMenuSelection" (which inhereted from discord.ui.Select) to the container, "discord.ui.View"
class helpMenuSelection(discord.ui.Select):
    def __init__(self):
        #here we can not do "self.options = [...]"
        #NOTICE in order to add our own options we need to call the parrent intializer
        #we can only do this by making our own "def __init__(self)" but this automaticly overrides the parent initalizer
        #meaning we need to call the parent initalizer itself in our own "def __init__(self)"
        #NOTICE "options" is not "self.options". in "super().__init__(...)", there is the parameter, "options=".
        #here "options" refers to an actual list of options so doing "self.options" returns an error
        options = [
            discord.SelectOption(label = 'Search', value = 'search'),
            discord.SelectOption(label = 'Profile', value = 'profile')
        ]
        super().__init__(placeholder = "Choose something you're confused about", options=options)
        #NOTICE we can't just define our own placeholder and options within our initalizer
        #however the parents initailzer has the functionality already built within it's own intializer
        #but also if we define our own initalizer in the child class, we overide the parent initalizer therefore overriding any functionality
        #hence we need to call the parent initalizer so we can make use of the functionality already built within the parent initliazer

    async def callback(self, interaction: discord.Interaction):
        #self.values is a list of selected values by the user
        #because we called the parent initalizer, we also inhereted this attribute
        #returning self.values itself would return a list so we get a direct value by doing "self.values[0]"
        #here we don't need to worry about multiple selections becuase our drop down doesn't have that implimentation
        #meaning each new select automaticly is the first value within the "self.values" list
        #so returning "self.values[0]" returns the selected value by the user and overirding it if they select another value
        if self.values[0] == 'search':
            #also need to check if the user thats interacting is the user themselves or someone else
            #make an embed function so we don't need to rewrite a lot of code
            #"discord.Embed" is a class and "embed" is an object of that class
            embed = embed_gen('Help | Search', interaction.user.avatar, random.choice(footer_text))
            embed.add_field(name = 'Anime', value = 'Search for your favorite Anime', inline = False)
            embed.add_field(name = 'Manga', value = 'Search for any Manga', inline = False)
            embed.add_field(name = 'Character', value = 'Searches up any Anime/Manga character', inline = False)
            await interaction.response.edit_message(embed = embed)
        if self.values[0] == 'profile':
            embed = embed_gen('Help | Profile', interaction.user.avatar, random.choice(footer_text))
            embed.add_field(name = 'Profile', value = "Shows your profile or creates one for you", inline = False)
            embed.add_field(name = 'View', value = "Lets you see other people's profiles")
            embed.add_field(name = 'Edit', value = "You finish setting up your profile using the 'Edit' command\nAllows you to edit: username, bio, bias, fav Anime/Manga, Anime you're watching/will watch/watched, Manga you're reading/will read/read", inline = False)
            embed.add_field(name = 'Delete', value = "Does what it says, delete's your profile", inline = False)
            await interaction.response.edit_message(embed = embed)


#NOTICE we dont do "class discord.ui.View"
#instead we inherete the methods and attributes from discord.ui.View
#and override any methods, attributes if needed
#so in helpMenu we are using the functionalities of discord.ui.View to help make the "help menu"
#also interestingly, it also says within the documention for discord.py that discord.ui.View must be inhereted in order to make a UI
class helpMenuContainer(discord.ui.View):
    #also this is the container, meaning it contains buttons, select menues, models, and anything related to UI in discord
    #we have to add our select menu into this container
    #we don't create any buttons, select menues, models, etc instead we only assign ones already built within "discord.Ui.Select"
    def __init__(self, user_id):
        super().__init__()
        #NOTICE here we store the interaction from the original event so we know which interaction we are working with
        #"interaction" is an object that refers to an event.
        #it stores information based on the event that occured, hence why its an object
        #it is not the message itself. the message contains an embed, meaning the embed is apart of the original message. hence we have to edit that.
        self.user_id = user_id
        self.add_item(helpMenuSelection()) #notice how we add an item and not create anything here

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            embed = embed_gen('Profile | This Is Not Your Command', interaction.user.avatar, random.choice(footer_text))
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True


#main class
#NOTICE commands.Cog meaning we inhereate the methods from commands.Cog (not the attributes because we did not do super().__init__(...))
#also NOTICE the last line -> "await bot.add_cog(helpCog(bot))". 
# this is not to mistake that "bot" is an boject of "commands.Cog", it is NOT.
# the bot object is created from "class myBot(commands.Bot)"
#in "class myBot(commands.Bot)", "myBot" inhereted all methods from "commands.Bot" (and all attributes from "commands.Bot" because of super().__init__(...)
#so "bot" is an object of the class "myBot"

class helpCog(commands.Cog):    
    #in classes, if the parameter holds another class, it inherets from that class
    #similarly, helpCog inherets the methods from commands.Cog
    #this is not to be confused with if a new object is made -> helpCog_object = helpCog(bot), that the "bot" inside MUST be apart of commands.Cog (which it's not)
    #helpCog ONLY just inheretes the methods from commands.Cog, when creating a new object of helpCog it does not mean that you need an object of "commands.Cog"
    #the reason why we add "bot" in the parameter when making a new object -> helpCog_object = helpCog(bot) is becuase of the __init__() inside of helpCog(commands.Cog)
    #which needs us to pass the bot into this class
    def __init__(self):
        #NOTICE the parameter is commands.Cog, the __init__ is independet of the __init__ from commands.Bot
        #here we essintaly create an attribute for the current object (self.bot) and set it to the "bot" parameter which will literly be the bot
        #meaning we store the actual bot object in "self.bot"
        super().__init__()

    #all commands need the decerator @app_commands.command and all functions need to be a courtine
    #the function name needs to be the same as the name from "@app_commands.command(name = '...', ...)"
    #also in the function we specify that interaction can only be from discord.Interaction meaning anything else will bring up an error
    @app_commands.command(name = 'help', description = 'Info on bot and commands')
    #make the cooldown functionaity
    #when the cooldown is triggered, the CommandOnCooldown error will be rasied.
    #that error will be an exception that we need to add functionality to
    #so that whenever this exepction appears, the bot sends a cooldown message
    @app_commands.checks.cooldown(1, 5.0, key = lambda interaction: (interaction.user.id))
    #ALSO note that the "cooldown" in "@app_commands.checks.cooldown" is esseitnaly a function. meaning that "key" is a parameter of that function
    #when we define our "lambda" for "key", the "cooldown" function itself uses that "lambda" function
    #"lambda" is esseintaly being used inside of the "cooldown" function. conceptualy, thats how "lambda" functions are directed to work
    #We use "lambda" whenever we need a small function only once
    #it esseintaly has the same functionality when you define a normal function
    #EXAMPLE (normal function)
    #def double(x):
    #   return x * 2
    #this is the same as
    #EXAMPLE (lambda function)
    #lambda x: x * 2
    #here the important structor is
    #lambda parameters: return_value
    #Here "key = lambda i: (i.guild_id, i.user.id)" just means that "key" is equal to a function
    #meaning we can replace lambda with a normal function that does the same thing as the lambda function
    #lambda takes in i as the parameter and returns "i.guild_id" and "i.user.id"
    #so the normal function would be
    #def normal_lambda(i):
    #   return (i.guild_id, i.user.id)
    #NOTICE the "(...)". our first example didnt have a tuple, thats becasue it wasnt necessary but here we need to return as a tupile
    #here the information is being stored as a tupile. the guild id and the interaction id (here now its only interaction id). if we didnt have it as a tupile
    #then it would essentialy be confusing on what value witihn the list refers to the interaction
    async def help(self, interaction: discord.Interaction):
        embed = embed_gen('Help | Menu', interaction.user.avatar, random.choice(footer_text))
        embed.add_field(name = 'What would you like help with?', value = 'Search\nProfile')
        #in order to check if the same user is interacting with a command
        #we can send the original interaction id to "helpMenuContainer"
        #then send that same interaction id (the original interaction id) to "helpMenuSelection"
        #then from there we can check if a user that's interacting with the selection menu has the same user id as the original user
        #this is like connecting everything together with a rope, binding everything together
        #we first send the interaction user id to the help menu container
        await interaction.response.send_message(embed=embed, view=helpMenuContainer(interaction.user.id))
    #NOTICE we've made a cooldown using the decorator for app command cooldowns "@app_commands.checks.cooldown(...)"
    #when this cooldown is trigged, an error will be raised. the error will be "CommandOnCooldown".
    #we can use an error decortator that listens for an error
    #and when an error is raised, it adds functionality to that specific error being raised (by checking if that error is an instance of the error we want to handel)
    @help.error # ERROR
    async def on_help_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        #I think this error triggers an interaction. Since interactions themseleves are NOT messages, and simply sort of like objects for the event thats happening
        #having an interaction here tells discord that an error event is happening, so make an object that handels that event.
        #NOTICE we check if the error instance is of "app_commands.CommandOnCooldown" and not "app_commands.AppCommandError"
        #if we look at the discord.py documentation, the "CommandOnCooldown" error is inhereted from "CheckFailure" which inherets from "AppCommandError"
        #meaning "AppCommandError" is esseitnaly the parent of both "CheckFailure" and "CommandOnCooldown"
        #so when we have the parameter set as "error: app_commands.AppCommandError", we can even check if the error is an instance of "app_commands.CheckFailure"
        #or to think of it another way, we can check any child error of the parent error, "AppCommandError"
        if isinstance(error, app_commands.CommandOnCooldown):
            #Since this error is an instance of CommandOnCooldown, natrualy it has the information on when to retry after. Hence we can do "error.retry_after"
            embed = embed_gen('Help | Cooldown', interaction.user.avatar, f'Retry after: {int(error.retry_after)} seconds')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        print(f'\nHELP command ERROR: {error}\n')
        embed = embed_gen('Help | Unknown Error', interaction.user.avatar, 'Fixing things up...')
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: object):
    #setup function is not apart of "discord.py", we need to make it ourseleves
    #but even though it isnt apart of "discord.py", "discord.py" still looks for and runs the asyncrious function "setup"
    #in main.py, we have setup_hook(). each cog is setup with "self.load_extension(...)"
    #meaning since self refers to the current object and the object we have is our bot
    #the bot loads the cog and looks for "setup(bot: object)" and then also passes itself onto the parameter "(bot: object)"
    #then it adds the cog and makes an object of the class helpCog
    #without it making an object of the class helpCog, it can not store itself into the class and wouldn't be functional
    await bot.add_cog(helpCog())