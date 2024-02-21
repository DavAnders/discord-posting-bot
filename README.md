# discord-posting-bot
Python 3.11 was used to make this. 3.12 causes issues.

You will need to replace the discord API token and setup a config.json file to use this bot.

Posts direct messages that are sent to the bot, but anonymously into the specified channel.
The idea was to be able to share thoughts or feelings without a name attached.

Users with moderator permissions should be able to set a keyword and channel, using:
!setkeyword keyword channelid.

The !post command should be sent in a DM to the bot, and uses the keyword to post to a channel.
This approach was used as a way to be able to differentiate between servers if the user is in mutiple servers
that the bot is also in.
!post command should be used as:
!post keyword message

Along with the anonymous message posting, there is a music functionality to the bot.
The commands for the music bot are typical to other music bots.

External libraries -
The bot uses yt-dlp and ffmpeg for the music side.
py-cord was used to handle the bot functionality.


Forgot to add, might be important if anyone intends on using this:

THe posting functionality could easily be enhanced with a censoring/filter option. I wouldn't recommend running it
without knowing or trusting the people using it without a filter.
