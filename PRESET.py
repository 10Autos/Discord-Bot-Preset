import discord
import os
import json
import asyncio


async def chelp(msg, args):
    if args[0].lower() == "list":
        await send_msg(msg, "These commands exist:", 30)
        for cmd in list(Command.commands.keys()):
            if Command.commands[cmd].enabled:
                await send_msg(msg, "`" + config["prefix"] + Command.commands[cmd].usage + "`: " + Command.commands[cmd].description, 30)
    else:
        if args[0] in Command.commands.keys() and Command.commands[args[1]].enabled:
            await send_msg(msg, "`" + config["prefix"] + Command.commands[args[1]].usage + "`: " + Command.commands[args[1]].usage, 10)
        else:
            await send_msg(msg, "This command doesn't exist!", 10)


async def settings(msg, args):
    if msg.author.guild_permissions.administrator:
        global config
        global file
        if len(args) == 0:
            await send_msg(msg, "These settings can be changed using `" + config["prefix"] + "settings <setting>`:", 30)
            await send_msg(msg, "prefix", 30)
        else:
            if args[0].lower() == "prefix":
                if len(args) == 1:
                    await send_msg(msg, "Please set a prefix using `" + config["prefix"] + "settings prefix <prefix>`:", 10)
                else:
                    config["prefix"] = args[1]
                    with open("config.json", "w") as file:
                        json.dump(config, file, indent=4)
                    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=config["prefix"] + "help"))
                    await send_msg(msg, "The prefix was changed successfully!", 10)
            else:
                await send_msg(msg, "This setting doesn't exist!", 10)
    else:
        await send_msg(msg, "You don't have permission to do this!", 10)


async def clear(msg, args):
    if msg.author.guild_permissions.manage_messages:
        if len(args) == 0 or not args[0].isdigit():
            await msg.channel.purge()
        else:
            await msg.channel.purge(limit=int(args[0]) + 1)
    else:
        await send_msg(msg, "You don't have permission to do this!", 10)


class Command:
    commands = {}

    command = ""
    usage = ""
    description = ""

    def __init__(self, command: str, usage: str, description: str, callback, enabled: bool = True):
        self.command = command
        self.usage = usage
        self.description = description
        self.enabled = enabled
        self.callback = callback
        Command.commands[self.command] = self


async def _send_msg(msg, content, delete_delay):
    new_msg = await msg.channel.send(content)
    if delete_delay is not None:
        await asyncio.sleep(delete_delay)
        await delete_msg(new_msg)


async def send_msg(msg, content, delete_delay=None):
    asyncio.create_task(_send_msg(msg, content, delete_delay))


async def delete_msg(msg):
    try:
        await msg.delete()
    except:
        return False
    return True


class Client(discord.Client):
    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=config["prefix"] + "help"))
        print(self.user.name + " is ready!")

    async def on_message(self, msg):
        if msg.content.startswith(config["prefix"]) and msg.guild and not msg.author.bot:
            args = msg.content[len(config["prefix"]):].split(" ")
            args[0] = args[0].lower()
            if args[0] in Command.commands.keys() and Command.commands[args[0]].enabled:
                if len(args) >= len(Command.commands[args[0]].usage.split(" ")):
                    await Command.commands[args[0]].callback(msg, args[1:])
                else:
                    await send_msg(msg, "Please use `" + config["prefix"] + Command.commands[args[0]].usage + "`!", 10)
            else:
                await send_msg(msg, "This command doesn't exist!", 10)
            await delete_msg(msg)


if __name__ == "__main__":
    if not os.path.exists("config.json"):
        with open("config.json", "w") as file:
            json.dump({"prefix": "-"}, file, indent=4)
    with open("config.json", "r") as file:
        config = json.load(file)

    # Command(command, usage, description, callback, active)
    Command("help", "help <command>|list", "This command will help you", chelp)
    Command("settings", "settings", "This command will change the settings", settings, False)
    Command("clear", "clear", "This command will clear all messages in this channel", clear, False)

    intents = discord.Intents.default()
    intents.members = True

    bot = Client(intents=intents)
    bot.run("KEY")
