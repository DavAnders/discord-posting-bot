from discord.ext import commands
import discord
import yt_dlp


class Video:
    def __init__(self, url):
        self.url = url
        self.stream_url = None
        self.title = "Unknown"
        self._fetch_video_info()

    def _fetch_video_info(self):
        ydl_opts = {
            'format': 'bestaudio',
            'quiet': True,
            'no_warnings': True,
            'extractaudio': True,
            'audioformat': "best",
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'verbose': True,
        }

        # these settings seem to work consistently. others not so much
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                video_info = ydl.extract_info(self.url, download=False)
                if 'entries' in video_info and len(video_info['entries']) > 0:
                    # Use the first search result
                    video_info = video_info['entries'][0]
                if 'url' in video_info:
                    self.stream_url = video_info['url']
                    self.title = video_info.get('title', self.title)
                else:
                    audio_info = next((format for format in video_info['formats'] if format['vcodec'] == 'none'), None)
                    if audio_info:
                        self.stream_url = audio_info['url']
            except Exception as e:
                print(f"Error fetching video info: {e}")



class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
    
    def check_queue(self, ctx):
        if self.song_queue[ctx.guild.id]:
            song = self.song_queue[ctx.guild.id].pop(0)  # Get the next song dictionary
            ctx.voice_client.play(song['source'], after=lambda e: self.check_queue(ctx))
            # Optionally send a message indicating the next song is playing
            self.bot.loop.create_task(ctx.send(f"Now playing: **{song['title']}**"))


    @commands.command(name="join")
    async def join(self, ctx):
        if not ctx.guild:  # ensure the command is used in a server
            return await ctx.send("This command can only be used in a server.")
        if ctx.author.voice is None:
            return await ctx.send("You are not connected to a voice channel.")
        elif ctx.voice_client is not None:
            await ctx.voice_client.move_to(ctx.author.voice.channel)
        else:
            await ctx.author.voice.channel.connect()

    @commands.command(name="play")
    async def play(self, ctx, *, search_query):
        if not ctx.guild:  # Ensure the command is used in a server
            return await ctx.send("This command can only be used in a server.")
        if ctx.author.voice is None:
            return await ctx.send("You are not connected to a voice channel.")

        if ctx.voice_client is None:
            await ctx.invoke(self.join)

        # determine if input is a URL or search query
        if not search_query.startswith(('http://', 'https://')):
            search_query = f"ytsearch:{search_query}"

        video = Video(search_query)  # use the Video class that can handle both URLs and searches
        if video.stream_url is None:
            await ctx.send("Could not retrieve video information.")
            return

        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }
        source = await discord.FFmpegOpusAudio.from_probe(video.stream_url, **FFMPEG_OPTIONS)
        song = {'source': source, 'title': video.title}

        self.song_queue.setdefault(ctx.guild.id, []).append(song)
        if not ctx.voice_client.is_playing():
            await ctx.send(f"**{video.title}** added to the queue and now playing.")
            self.check_queue(ctx)
        else:
            await ctx.send(f"**{video.title}** added to the queue.")



    @commands.command(name='disconnect')
    async def disconnect(self, ctx):
        # disconnects the bot from the voice channel
        await ctx.voice_client.disconnect()

    @commands.command(name='pause')
    async def pause(self, ctx):
        # pauses song playing
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        else:
            await ctx.send("Nothing is playing to pause.")
    
    @commands.command(name='resume')
    async def resume(self, ctx):
        # resume/unpause song
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
        else:
            await ctx.send("The audio is not paused.")
    
    @commands.command(name='stop')
    async def stop(self, ctx):
        # stops current song and clears the queue
        ctx.voice_client.stop()
        self.song_queue[ctx.guild.id] = []
    
    @commands.command(name='queue')
    async def queue(self, ctx):
        # displays the current song queue with titles.
        if ctx.guild.id in self.song_queue and self.song_queue[ctx.guild.id]:
            queue_msgs = [f"{idx}. {song['title']}" for idx, song in enumerate(self.song_queue[ctx.guild.id], start=1)]
            queue_str = '\n'.join(queue_msgs)
            await ctx.send(f"Current queue:\n{queue_str}")
        else:
            await ctx.send("The queue is currently empty.")

    
    @commands.command(name='skip')
    async def skip(self, ctx):
        # skips the currently playing song
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()  # stopping current song will trigger check_queue
            await ctx.send("Song skipped.")
        else:
            await ctx.send("No song is currently playing.")


def setup(bot):
    bot.add_cog(Music(bot))
