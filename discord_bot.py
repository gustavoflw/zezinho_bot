import os
import discord
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
from unidecode import unidecode

from mimic import Mimic
from youtube_handler import YoutubeHandler
from message_history import MessageHistory
from bot_print import print_with_colors as print

class DiscordBot(discord.Client):
    def __init__(self, intents, token):
        print(f'- Initializing Discord bot...', color='cyan')
        super().__init__(intents=intents)

        self.bot_user_id = '1215127308587900939'
        self.max_characters = 1900
        self.connected_voice_channels = []
        self.mimicking = False # Flag to indicate if the bot is currently mimicking a user
        self.t_mimic_start = None # Timestamp when the bot started mimicking
        self.timeout_mimicking = 30 # How long the bot will mimic a user before stopping

        print(f'- Running bot...', color='cyan')
        self.run(token)

    async def on_ready(self):
        print(f'- [ON_READY] {self.user} has connected to Discord!', color='cyan')
        channels = self.get_text_channels()

        for channel in channels:
            if 'bot' in str(channel.name).lower():
                await self.send_message_in_channel('pai ta on', channel.id)

    async def on_message(self, message: discord.Message):
        print(f'- [ON_MESSAGE] {message.author} in {message.channel}: {message.content}', color='cyan')

        if len(message.content) == 0:
            print(f'- Empty message, ignoring...', color='cyan')
            return

        mimicked_this_time = False

        first_char = message.content[0]

        if first_char.isalnum():
            message_history = MessageHistory(message.author.id, message.channel.id)
            message_history.append_message(message.author.name, message.created_at, message.channel.id, message.content)

        if first_char == ';':
            command = message.content[1:].split(' ')
            if command[0] == 'mimic':
                mentions = message.mentions
                if len(mentions) > 0:
                    target_user_id = message.mentions[0].id
                    await self.mimic_user(target_user_id, message.channel.id)
                    self.t_mimic_start = datetime.now().timestamp()
                    self.mimicking = True
                    mimicked_this_time = True
            elif command[0] == 'question':
                question = ' '.join(command[1:])
                mimic = Mimic(message.author.id, message.channel.id)
                response = mimic.question(question)
                await self.send_message_in_channel(response, message.channel.id)
            elif command[0] == 'play':
                to_play = ' '.join(command[1:])
                await self.on_play(to_play, message.channel, message.author)
            elif command[0] == 'stop':
                await self.on_stop(message.author.voice.channel)

        if self.mimicking and not mimicked_this_time:
            if datetime.now().timestamp() - self.t_mimic_start > self.timeout_mimicking:
                print(f'- Timeout for mimicking has been reached', color='cyan')
                self.mimicking = False
            else:
                await self.mimic_user(message.author.id, message.channel.id)

    async def on_play(self, to_play: str, text_channel: discord.TextChannel, user: discord.User):
        try:
            print(f'- Playing {to_play}', color='cyan')

            already_connected = False
            for connected_voice_channel in self.connected_voice_channels:
                if connected_voice_channel.channel.id == user.voice.channel.id:
                    print(f'- Already connected to voice channel {connected_voice_channel.channel.id}', color='cyan')
                    already_connected = True
                    break
            if not already_connected:
                connected_voice_channel = await user.voice.channel.connect()
                self.connected_voice_channels.append(connected_voice_channel)

            file_path = YoutubeHandler().play(to_play)
            connected_voice_channel.play(discord.FFmpegPCMAudio(file_path))
            await self.send_message_in_channel(f'soltando o som: {to_play}', text_channel.id)
        except Exception as exception:
            print(f'- [ERROR] {exception}', color='red')
            await self.send_message_in_channel(f'ja to tocando bro', text_channel.id)

    async def on_stop(self, user_voice_channel: discord.VoiceChannel):
        try:
            print(f'- Stopping playback', color='cyan')
            for connected_voice_channel in self.connected_voice_channels:
                if connected_voice_channel.channel.id == user_voice_channel.id:
                    await connected_voice_channel.disconnect()
                    self.connected_voice_channels.remove(connected_voice_channel)
                    await self.send_message_in_channel(f'vamos ficar em silencio ne', connected_voice_channel.channel.id)
                    break
        except Exception as exception:
            print(f'- [ERROR] {exception}', color='red')
            await self.send_message_in_channel(f'deu algo errado, algum de nos ta burro', connected_voice_channel.channel.id)

    async def mimic_user(self, user_id, channel_id):
        if str(user_id) == str(self.bot_user_id):
            print(f'- Not mimicking myself, duhh', color='cyan')
            return

        print(f'- Mimicking target user id: {user_id}', color='cyan')
        mimic = Mimic(user_id, channel_id)
        tries = 0
        success = False
        while tries < 5:
            try:
                mimic_response = mimic.mimic()
                success = True
                await self.send_message_in_channel(mimic_response, channel_id)
                break
            except Exception as e:
                print(f'- [MIMIC FAILURE] {e}', color='red')
                tries += 1
                sleep(5)
        if not success:
            await self.send_message_in_channel('SOU MTO BURRO MANO!!!', channel_id)

    async def send_message_in_channel(self, message, channel_id):
        print(f'- Sending message in channel {channel_id} {message}', color='cyan')
        try:
            channel = self.get_channel(channel_id)
        except Exception as exception:
            print(f'- [ERROR] {exception}', color='red')
            return

        if len(message) > self.max_characters:
            message = message.split(' ')
            message_list = []
            message_temp = ''
            for word in message:
                if len(message_temp) + len(word) < self.max_characters:
                    message_temp += word + ' '
                else:
                    message_list.append(message_temp)
                    message_temp = word + ' '
        else:
            message_list = [message]

        for m in message_list:
            print(f'- Message (after splitting): {m}', color='cyan')
            try:
                await channel.send(m)
            except Exception as exception:
                    print(f'- [ERROR] {exception}', color='red')

    def get_channels(self):
        print(f'- Getting all channels...', color='cyan')
        channels = self.get_all_channels()
        return channels

    def get_text_channels(self):
        print(f'- Getting all text channels...', color='cyan')
        all_channels = self.get_channels()
        channels = [channel for channel in all_channels if channel.type == discord.ChannelType.text]
        print(f'- Channels:', color='cyan')
        [print(f'    - {channel.name} (id: {channel.id}), type: {channel.type}', color='cyan') for channel in channels]
        return channels

if __name__ == '__main__':
    load_dotenv()
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    bot = DiscordBot(intents=intents, token=os.getenv('DISCORD_TOKEN'))
