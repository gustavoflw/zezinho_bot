import csv
import os
import random
from datetime import datetime

from bot_print import print_with_colors as print

class MessageHistory:
    def __init__(self, user_id, channel_id):
        print(f'- Creating MessageHistory(user_id={user_id}), channel_id={channel_id}', color='magenta')
        self.user_id = user_id
        self.channel_id = channel_id

        self.user_ids_to_ignore = ['1215127308587900939']

        self.path_message_history_dir = os.path.join(os.environ.get('HOME'), 'message_history')
        self.name_csv_file = f'{self.user_id}.csv'
        self.path_csv_file = os.path.join(self.path_message_history_dir, self.name_csv_file)
        os.makedirs(self.path_message_history_dir, exist_ok=True)

        self.csv_columns = ['user_id', 'user_name', 'timestamp', 'channel_id', 'message']

        self.create_csv_file()

    def append_message(self, user_name, timestamp, channel_id, message):
        with open(self.path_csv_file, mode='a') as file:
            print(f'-----> Appending message to {self.name_csv_file}', color='magenta')
            writer = csv.DictWriter(file, fieldnames=self.csv_columns)
            row = {'user_id': self.user_id, 'user_name': user_name, 'timestamp': timestamp, 'channel_id': channel_id, 'message': message}
            print(f'       - {list(row.values())}', color='magenta')
            writer.writerow(row)

    def get_last_n_messages_in_channel(self, n):
        '''
        Reads all .csv files in the current directory and append them to the same list
        Orders them by timestamp
        Then, it returns the last N messages that correspond to the channel_id
        '''
        
        print(f'- Getting last {n} messages for channel {self.channel_id}', color='magenta')
        messages = []
        for filename in os.listdir(self.path_message_history_dir):
            path_file = os.path.join(self.path_message_history_dir, filename)
            if filename.endswith('.csv'):
                with open(path_file, mode='r') as csv_file:
                    reader = csv.DictReader(csv_file)
                    rows = [row for row in reader]
                    [messages.append(row) for row in rows if str(row['channel_id']) == str(self.channel_id)]
        messages = sorted(messages, key=lambda x: datetime.strptime(x['timestamp'], "%Y-%m-%d %H:%M:%S.%f%z"))
        # messages = [message for message in messages if str(message['user_id']) not in self.user_ids_to_ignore]
        messages = messages[-n:] if len(messages) > n else messages
        messages = [message for message in messages if message['message'][0].isalpha()]
        [print(f'       - {list(message.values())}', color='magenta') for message in messages]
        print(f'>>> len(last_n_messages_in_channel): {len(messages)}', color='magenta')
        return messages

    def get_random_n_messages(self, n):
        with open(self.path_csv_file, mode='r') as file:
            print(f'- Getting random {n} messages from {self.path_csv_file}', color='magenta')
            reader = csv.DictReader(file)
            messages = [row for row in reader]
            messages = [message for message in messages if message['message'][0].isalpha()]
            messages = messages if len(messages) < n else random.sample(messages, n)
            [print(f'       - {list(message.values())}', color='magenta') for message in messages]
            print(f'>>> len(random_n_messages): {len(messages)}', color='magenta')
            return messages

    def create_csv_file(self):
        if not os.path.exists(self.path_csv_file):
            print(f'- Creating file {self.path_csv_file}', color='magenta')
            with open(self.path_csv_file, mode='w') as file:
                writer = csv.DictWriter(file, fieldnames=self.csv_columns)
                writer.writeheader()
        else:
            print(f'- File {self.path_csv_file} already exists', color='magenta')

# Test
if __name__ == '__main__':
    user_id = 1155000744865439875
    channel_id = 1215156974233198602
    N = 5

    # To test getting user messages:
    # message_history = MessageHistory(user_id, None)
    # message_history.create_csv_file()
    # message_history.append_message('user_name', datetime.now(), 'channel_id', 'message')
    # print(f"- Random {N} messages:")
    # [print(f'- {message}') for message in message_history.get_random_n_messages(N)]

    # To test getting last N messages in a channel:
    message_history = MessageHistory(user_id, channel_id)
    # for i in range(7):
        # message_history.append_message('user_name', datetime.now(), channel_id, f'message {i}')
    message_history.get_last_n_messages_in_channel(N)
