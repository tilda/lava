import discord
from discord.ext import commands
from ruamel.yaml import YAML
import logging

rlog = logging.getLogger()
rlog.setLevel(logging.INFO)
# set format
fmt = logging.Formatter('[{levelname}] {name}: {message}', style='{')
stream = logging.StreamHandler()
stream.setFormatter(fmt)
rlog.addHandler(stream)

yaml = YAML(typ='safe')
conf_file = open('config.yaml').read().rstrip()
config = yaml.load(conf_file)

class HahaYes(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        yaml = YAML(typ='safe')
        self.config = yaml.load(open('config.yaml').read().rstrip())

    async def on_ready(self):
    	rlog.info("""
    		                          .'  .
                         .'.'.' .
                        .`.'.`'.
                       ..'..'.`'
                       `,'....`
                      `' ..'`.
                     `'``''`.
                     .'.``'`
                  .'`..'''`.
                    ````.'`
                  xl""``""lx
                 X8Xxx..xxX8X
                 8X8bdX8bd8X8
                dX8Xbd8XbdX8Xb
               dX8Xbd8X8XbdX8Xb
              dX8Xbd8X8X8XbdX8Xb
            .dX8Xbd8X8X8X8XbdX8Xb.
          .d8X8Xbd8X8X8X8X8XbdX8X8b.
      _.-dX8X8Xbd8X8X8X8X8X8XdbX8X8Xb-._
   .-d8X8X8X8bdX8X8X8X8X8X8X8X8db8X8X8X8b-.
.-d8X8X8X8X8bdX8X8X8X8X8X8X8X8X8db8X8X8-RG-b-.""")
      rlog.info("Hi. I'm Lava.")

bot = HahaYes(command_prefix=commands.when_mentioned_or(config['prefix']),
              description='A simple music bot.',
              pm_help=None)
try:
    bot.run(config['token'])
except discord.LoginFailure:
    rlog.critical('Login failed.')
    rlog.critical('Please check your token.')
    sys.exit(1)
