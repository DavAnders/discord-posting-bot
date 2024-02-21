import discord
import json
import music
from discord.ext import commands
from auth import token, url, channel, newtesttoken

config_file_path = "config.json"
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.voice_states= True
intents.guild_messages = True
intents.guild_typing = True
intents.guilds = True

#client = discord.Client(intents=intents) <-- client vs commands
bot = commands.Bot(command_prefix="!", intents=intents)

def load_config():
    try:
        with open(config_file_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return {"keywords": {}}

def save_config(config):
    with open(config_file_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)

@bot.command(name='setkeyword')
@commands.has_permissions(manage_guild=True)
async def set_keyword(ctx, keyword: str, new_channel: discord.TextChannel):
    config = load_config()
    # check if the keyword already exists
    if keyword in config.get("keywords", {}):
        await ctx.send("This keyword is already in use. Please choose a different one.")
        return

    # update the configuration with the new keyword
    config["keywords"][keyword] = {
        "server_id": str(ctx.guild.id),
        "channel_id": str(new_channel.id)
    }
    save_config(config)
    await ctx.send(f"Keyword `{keyword}` set for anonymous posts to {new_channel.mention}.")




@set_keyword.error
async def set_keyword_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        # handle missing permissions
        await ctx.send("You do not have the necessary permissions to set the keyword and channel.")
    elif isinstance(error, commands.BadArgument):
        # handle bad arguments
        await ctx.send("Please provide a valid text channel.")
    else:
        # any other uncaught errors
        await ctx.send("An error occurred while setting the keyword and channel. Please try again.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    # ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # check if the message is a DM
    if isinstance(message.channel, discord.DMChannel):
        # if the message starts with "!post", it could be an attempt to use the posting feature
        if message.content.startswith("!post"):
            # split the message to analyze its parts: command, keyword, and the message content
            parts = message.content.split(maxsplit=2)
            # check if the message follows the expected format: "!post keyword The message"
            if len(parts) >= 3:
                _, keyword, content = parts

                # load the bot's configuration to get the mapping of keywords to channels
                config = load_config()
                keywords = config.get("keywords", {})
                
                # check if the provided keyword is recognized (i.e., it exists in the configuration)
                keyword_info = keywords.get(keyword)
                if keyword_info:
                    # retrieve the target channel based on the keyword configuration
                    target_channel = bot.get_channel(int(keyword_info["channel_id"]))
                    if target_channel:
                        await target_channel.send(content)
                        await message.author.send(f"Your message was posted to {target_channel.mention} using keyword `{keyword}`!")
                        return
                    else:
                        # handle the case where the target channel could not be found
                        await message.author.send("Couldn't find the target channel for your keyword. It might have been deleted.")
                        return
                else:
                    # inform the user if the keyword used is not recognized
                    await message.author.send("The keyword used is not recognized. Please use a valid keyword.")
                    return
            else:
                # if the message does not follow the correct format
                await message.author.send(
                    "Hello! If you want me to post a message anonymously, "
                    "please use the format: `!post keyword Your message here.`"
                )
                return
        else:
            # for any message in a DM that doesn't start with "!post"
            await message.author.send(
                "Hello! To post an anonymous message, start your message with `!post keyword Your message here.`"
            )
            return

    # ensure other commands are processed
    await bot.process_commands(message)





def main():
    try:
        bot.load_extension('music')
    except Exception as e:
        print(f'Failed to load extension music.\n{e}')

    bot.run(newtesttoken)

if __name__ == "__main__":
    main()