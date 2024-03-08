import os
import discord
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
from unidecode import unidecode

from bot_print import print_with_colors as print
from message_history import MessageHistory
from mimic import Mimic

class DiscordBot(discord.Client):
    def __init__(self, intents, token):
        print(f'- Initializing Discord bot...', color='cyan')
        super().__init__(intents=intents)

        self.bot_user_id = '1215127308587900939'
        self.max_characters = 1900
        print(f'- Bot user id: {self.bot_user_id}', color='cyan')
        print(f'- Max characters: {self.max_characters}', color='cyan')

        print(f'- Running bot...', color='cyan')
        self.run(token)

        self.mimicking = False # Flag to indicate if the bot is currently mimicking a user
        self.t_mimic_start = None # Timestamp when the bot started mimicking
        self.timeout_mimicking = 30 # How long the bot will mimic a user before stopping

    async def on_ready(self):
        print(f'- [ON_READY] {self.user} has connected to Discord!', color='cyan')
        channels = self.get_text_channels()

        target_channel = None
        for channel in channels:
            if 'bot' in str(channel.name).lower():
                target_channel = channel
                break
        if target_channel is None:
            target_channel = channels[0]

        await self.send_message_in_channel('O pai ta on', target_channel.id)

    async def on_message(self, message):
        print(f'- [ON_MESSAGE] {message.author} in {message.channel}: {message.content}', color='cyan')

        message_history = MessageHistory(message.author.id, message.channel.id)
        message_history.append_message(message.author.name, message.created_at, message.channel.id, message.content)

        # if self.mimicking:
        #     if datetime.now().timestamp() - self.t_mimic_start > self.timeout_mimicking:
        #         print(f'- Timeout for mimicking has been reached', color='cyan')
        #         self.mimicking = False

        # if str(message.author.id) != str(self.bot_user_id):
        #     if message.content.startswith('!mimic'):
        #         mentions = message.mentions
        #         if len(mentions) > 0:
        #             target_user_id = message.mentions[0].id
        #             await self.mimic_user(target_user_id, message.channel.id)
        #             self.t_mimic_start = datetime.now().timestamp()
        #             self.mimicking = True
        #     else:
        #         await self.mimic_user(message.author.id, message.channel.id)

    # async def mimic_user(self, user_id, channel_id):
    #     print(f'- Mimicking target user id: {user_id}', color='cyan')
    #     mimic = Mimic(user_id, channel_id)
    #     tries = 0
    #     success = False
    #     while tries < 5:
    #         try:
    #             mimic_response = mimic.mimic()
    #             success = True
    #             await self.send_message_in_channel(mimic_response, channel_id)
    #             break
    #         except Exception as e:
    #             print(f'- [MIMIC FAILURE] {e}', color='red')
    #             tries += 1
    #             sleep(5)
    #     if not success:
    #         await self.send_message_in_channel('SOU MTO BURRO MANO!!!', channel_id)

    async def send_message_in_channel(self, message, channel_id):
        print(f'- Sending message in channel {channel_id} {message}', color='cyan')
        channel = self.get_channel(channel_id)

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
            await channel.send(m)

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
