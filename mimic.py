import os
import json
from unidecode import unidecode
from dotenv import load_dotenv
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage


from message_history import MessageHistory
from bot_print import print_with_colors as print

class Mimic:
    def __init__(self, user_id, channel_id):
        print(f'- Initializing Mimic bot for user {user_id} in channel {channel_id}', color='yellow')
        self.target_id = user_id # The user id of the target
        self.channel_id = channel_id # The channel id where the bot is going to interact

        self.num_channel_last_messages = 10 # The number of messages from the channel that the bot will use to generate a response (including messages from all users since the bot was first triggered)
        self.num_target_historic_messages = 10 # The number of messages of the target that the bot will use to generate a response (only the messages from the target)

        self.message_history = MessageHistory(self.target_id, self.channel_id)

        self.context = ["Você é um bot chamado Zezinho, que fala PORTUGUES.",
                        "Tem uma conversa acontecendo no chat."]
        self.context = '\n'.join(self.context)
        print(f"- CONTEXT:\n{self.context}", color='yellow')

        load_dotenv()

        self.model = os.getenv('MISTRAL_AI_MODEL')  
        self.client = MistralClient(api_key=os.getenv('MISTRAL_AI_API_KEY'))

    def question(self, question: str) -> str:
        prompt = f"{self.context}\n\nAlguem fez uma pergunta no chat: '{question}'"
        prompt = f"{prompt} Responda em formato JSON com a chave 'response' e o valor sendo a resposta."
        print(f"- PROMPT:\n{prompt}", color='bold')

        message = ChatMessage(role="user", content=prompt)
        chat_response = self.client.chat(model=self.model, messages=[message], max_tokens=150, temperature=0.7, top_p=0.9, safe_mode=False)
        chat_response_content = chat_response.choices[0].message.content
        print(chat_response_content, color='green')

        parsed_response = self.parse_response_content(str(chat_response_content))
        print(f"- PARSED RESPONSE: {parsed_response}", color='yellow')

        return parsed_response

    def mimic(self) -> str:
        last_n_messages_in_channel = self.message_history.get_last_n_messages_in_channel(self.num_channel_last_messages)
        random_n_target_messages = self.message_history.get_random_n_messages(self.num_target_historic_messages)

        # Format the last n messages from the channel
        channel_msgs_formatted = []
        for message in last_n_messages_in_channel:
            user_id = message['user_id']
            user_name = message['user_name']
            timestamp = message['timestamp']
            channel_id = message['channel_id']
            message_content = message['message']
            message_formatted = f"- [{user_name}]: {message_content}"
            channel_msgs_formatted.append(message_formatted)
        channel_msgs_formatted = ['Essas sao as mensagens mais recentes do chat:'] + channel_msgs_formatted
        channel_msgs_formatted = '\n'.join(channel_msgs_formatted)
        print(f"- CHANNEL_MSGS:\n{channel_msgs_formatted}", color='yellow')

        # Format the last n messages from the target
        keywords = []
        for message in random_n_target_messages:
            user_id = message['user_id']
            user_name = message['user_name']
            timestamp = message['timestamp']
            channel_id = message['channel_id']
            message_content = message['message']
            message_formatted = f"- [ALVO]: {message_content}"
            keywords = keywords + message_content.split(' ')
        keywords = list(set(keywords))
        keywords = [keyword.strip() for keyword in keywords if len(keyword) > 2]
        keywords = ', '.join(keywords)

        keywords = 'Aqui estao algumas palavras-chave, para que voce se baseie no estilo de escrita:' + keywords
        print(f"- KEYWORDS:\n{keywords}", color='yellow')

        prompt = f"{self.context}\n\n{channel_msgs_formatted}"
        prompt = f"{prompt}\n\n{keywords}"
        prompt = f"{prompt}\n\n\n*** Não responda em mais de uma frase. Apenas baseie-se no estilo de escrita das frases do alvo."
        prompt = f"{prompt} Se esforce para nao repetir ideias no contexto da conversa e responda em uma frase CURTA."
        prompt = f"{prompt} Responda em formato JSON com a chave 'response' e o valor sendo a resposta."
        print(f"- PROMPT:\n{prompt}", color='bold')

        message = ChatMessage(role="user", content=prompt)
        chat_response = self.client.chat(model=self.model, messages=[message], max_tokens=200, temperature=0.7, top_p=0.9)
        chat_response_content = chat_response.choices[0].message.content
        print(chat_response_content, color='green')

        parsed_response = self.parse_response_content(str(chat_response_content))
        print(f"- PARSED RESPONSE: {parsed_response}", color='yellow')

        return parsed_response

    def parse_response_content(self, response_content: str) -> str:
        response_content = response_content.strip()

        characters = ['\n', '\t', '\r', '\\']
        for c in characters:
            response_content = response_content.replace(c, '')

        if isinstance(response_content, str) and response_content[-1] != '}' and response_content[-2] != '"':
            response_content = response_content + '"}'

        print(response_content)

        # Convert to Json
        response_content = json.loads(response_content)
        response = str(response_content['response']).replace('\n', ' ')

        return response

# Test
if __name__ == '__main__':
    mimic = Mimic(123, 123)
