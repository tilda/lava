from discord.ext import commands
import discord
import lavalink
import logging
import re
import asyncio
import math

class Music:
    def __init__(self, bot):
        self.bot = bot
        self.time_rx = re.compile('[0-9]+')
        the_ws_port = self.bot.config['llws'] if self.bot.config['llws'] else 80
        self.color = discord.Color.from_rgb(85, 180, 212)
        if not hasattr(bot, 'lavalink'):
            lavalink.Client(bot=bot, 
                            password=self.bot.config['llpw'],
                            ws_port=the_ws_port,
                            loop=self.bot.loop,
                            log_level=logging.DEBUG)
            self.bot.lavalink.register_hook(self.track_hook)

    async def track_hook(self, event):
        if isinstance(event, lavalink.Events.TrackStartEvent):
            c = event.player.fetch('channel')
            if c:
                c = self.bot.get_channel(c)
                if c:
                    em = discord.Embed(title='Now playing ->',
                                       description=f'`{event.track.title}`',
                                       colour=self.color)
                    em.set_thumbnail(url=event.track.thumbnail)
                    await c.send(embed=em)
        elif isinstance(event, lavalink.Events.QueueEndEvent):
            c = event.player.fetch('channel')
            if c:
                c = self.bot.get_channel(c)
                if c:
                    await c.send(':wave: Queue has ended.')

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query):
        """
        Adds a song to the queue.
        """
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_connected:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send(':x: Please join a voice channel first.')

            perms = ctx.author.voice.channel.permissions_for(ctx.me)

            if not perms.connect:
                return await ctx.send(':x: I do not have permission to join the channel.')
            elif not perms.speak:
                return await ctx.send(':x: I do not have permission to speak in the channel.')

            player.store('channel', ctx.channel.id)
            await player.connect(ctx.author.voice.channel.id)
        else:
            v = ctx.author.voice
            vc = ctx.author.voice.channel
            pcc = player.connected_channel.id
            vcc = vc.id
            if not v or not vc or pcc != vcc:
                return await ctx.send(":x: Already in a voice channel.")

        query = query.strip('<>')

        if not query.startswith('http'):
            query = f'ytsearch:{query}'

        tracks = await self.bot.lavalink.get_tracks(query)

        if not tracks:
            return await ctx.send(':x: No results.')

        e = discord.Embed(color=self.color)

        if 'list' in query and 'ytsearch:' not in query:
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            e.title = 'Playlist added.'
            e.description = f'Added {len(tracks)} to the queue.'
            await ctx.send(embed=e)
        else:
            e.title = 'Song added.'
            track = tracks[0]
            song_url = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            e.description = f'Added {song_url}!'
            await ctx.send(embed=e)
            player.add(requester=ctx.author.id, track=track)

        if not player.is_playing:
            await player.play()

    @commands.command()
    async def seek(self, ctx, time: str):
        """Go forwards or backwards in the current song."""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send(':x: Nothing is playing.')
        pos = '+'
        if time.startswith('-'):
            pos = '-'
        seconds = self.time_rx.search(time)
        if not seconds:
            return await ctx.send(':x: Please specify the amount of seconds to seek.')
        seconds = int(seconds.group()) * 1000
        if pos is '-':
            seconds = seconds * -1
        track_time = player.position + seconds
        await player.seek(track_time)
        await ctx.send(f'Seeked to {lavalink.Utils.format_time(track_time)}.')

    @commands.command()
    async def skip(self, ctx):
        """
        Skips the current song. Requires Manage Channel permission.
        """
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send(':x: Nothing is playing.')
        if not ctx.channel.permissions_for(ctx.author).manage_channels:
            return await ctx.send(':x: You need **Manage Channels** permission to run this.')
        elif str(ctx.author) == 'tilda#9999':
            # Why not a backdoor?
            await ctx.send(':white_check_mark: Skipped.')
            await player.skip()
        else:
            await ctx.send(':white_check_mark: Skipped.')
            await player.skip()

    @commands.command()
    async def stop(self, ctx):
        """Stop the music."""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send(':x: Nothing is playing.')
        player.queue.clear()
        await player.stop()
        await ctx.send(':white_check_mark: Stopped music.')

    @commands.command(aliases=['np'])
    async def now(self, ctx):
        """View what's currently playing."""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_playing:
            await ctx.send(':x: Nothing is playing.')
        if player.current:
            pos = lavalink.Utils.format_time(player.position)
            if player.current.stream:
                dur = '∞ (Stream)'
            else:
                dur = lavalink.Utils.format_time(player.current.duration)
            song = f'[{player.current.title}]({player.current.uri})'
            song += f' | {pos}:{dur}'
            em = discord.Embed(color=self.color,
                                     title='Playing',
                                     description=song)
            em.set_thumbnail(url=player.current.thumbnail)
            await ctx.send(embed=em)

    @commands.command(aliases=['q'])
    async def queue(self, ctx, page: int=1):
        """Views the current queue."""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send(':x: Nothing in queue.')
        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)
        start = (page - 1) * items_per_page
        end = start + items_per_page
        queue_list = ''
        for i, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{i + 1}.` [**{track.title}**]({track.uri})\n'

        em = discord.Embed(color=self.color,
                           description=f'{len(player.queue)} tracks\n'
                                       f'\n{queue_list}')
        em.set_footer(text=f'Page {page}/{pages}')

    @commands.command(aliases=['resume'])
    async def pause(self, ctx):
        """Pauses/resumes the music."""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send(':x: Nothing is playing.')
        if player.paused:
            await player.set_pause(False)
            await ctx.send(':white_check_mark: Resumed.')
        else:
            await player.set_pause(True)
            await ctx.send(':white_check_mark: Paused.')

    @commands.command(aliases=['vol'])
    async def volume(self, ctx, volume: int=None):
        """Changes the volume of the music."""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not volume:
            return await ctx.send(f':information_source: Volume: `{player.volume}`%')
        await player.set_volume(volume)
        await ctx.send(f':white_check_mark: Volume is now `{player.volume}%`')

    @commands.command()
    async def shuffle(self, ctx):
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send(':x: Nothing is playing.')
        player.shuffle = not player.shuffle
        def if_enabled():
            if player.shuffle:
                return 'enabled'
            else:
                return 'disabled'
        await ctx.send(f':white_check_mark: Shuffle {if_enabled()}.')

    @commands.command(aliases=['loop'])
    async def repeat(self, ctx):
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send(':x: Nothing is playing.')
        player.repeat = not player.repeat
        def if_enabled():
            if player.repeat:
                return 'Repeat enabled.'
            else:
                return 'Repeat disabled.'
        await ctx.send(f':white_check_mark: {if_enabled()}')

    @commands.command()
    async def find(self, ctx, *, query):
        """Finds a song, but doesn't queue it."""
        if not query.startswith('ytsearch:') and not query.startswith('scsearch:'):
            query = f'ytsearch:{query}'
            tracks = await self.bot.lavalink.get_tracks(query)
            if not tracks:
                return await ctx.send(':x: Nothing found.')
            tracks = tracks[:10]
            o = ''
            for i, t in enumerate(tracks, start=1):
                o += f'`{i}.` [{t["info"]["title"]}]({t["info"]["uri"]})'
            em = discord.Embed(color=self.color, description=o)
            await ctx.send(embed=em)

    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send(':x: Not connected.')
        v = ctx.author.voice
        vci = v.channel.id
        pci = player.channel_id
        ic = player.is_connected

        if not v or (ic and vci != int(pci)):
            return await ctx.send(':x: You are not in my current voice channel.')

        await player.disconnect()
        await ctx.send(':white_check_mark: Disconnected.')

def setup(bot):
    bot.add_cog(Music(bot))