"""
Module to (un|re| )load "cogs" (aka extensions).

Some code in this module is (c) 2018 slice.
"""
from discord.ext import commands
import discord
import traceback

class LoadExts:
    def __init__(self, bot):
        self.bot = bot

    @classmethod
    def codeblock(code: str, *, lang: str = '', escape: bool = True) -> str:
        """
        Constructs a Markdown codeblock.
        Parameters
        ----------
        code : str
            The code to insert into the codeblock.
        lang : str, optional
            The string to mark as the language when formatting.
        escape : bool, optional
            Prevents the code from escaping from the codeblock.
        Returns
        -------
        str
            The formatted codeblock.
        """
        return "```{}\n{}\n```".format(lang, escape_backticks(code) if escape else code)

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, *exts: str):
        """Loads a cog."""
        for ext in exts:
            try:
                self.bot.load_extension(f'cogs.{ext}')
            except ModuleNotFoundError:
                return await ctx.send(':x: Cog not found.')
            except Exception:
                return await ctx.send(codeblock(traceback.format_exc()))
            else:
                await ctx.send(f':white_check_mark: Cog `{ext}` loaded.')

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, *exts: str):
        """Unloads a cog."""
        for ext in exts:
            self.bot.unload_extension(f'cogs.{ext}')
            await ctx.send(f':white_check_mark: Unloaded `{ext}`.')

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *exts: str):
        for ext in exts:
            try:
                self.bot.unload_extension(f'cogs.{ext}')
                self.bot.load_extension(f'cogs.{ext}')
            except ModuleNotFoundError:
                return await ctx.send(':x: Cog not found.')
            except Exception:
                return await ctx.send(codeblock(traceback.format_exc))
            else:
                await ctx.send(f':white_check_mark: Cog `{ext}` reloaded.')

def setup(bot):
    bot.add_cog(LoadExts(bot))