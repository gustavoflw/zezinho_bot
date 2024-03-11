import os
import re
import json
from unidecode import unidecode
from dotenv import load_dotenv
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage


from message_history import MessageHistory
from bot_print import print_with_colors as print

class Mimic:
    def __init__(self, user_id, channel_id, num_channel_last_messages=1, num_target_historic_messages=10):
        print(f'- Initializing Mimic bot for user {user_id} in channel {channel_id}', color='yellow')
        self.target_id = user_id # The user id of the target
        self.channel_id = channel_id # The channel id where the bot is going to interact

        self.num_channel_last_messages = 1 # The number of messages from the channel that the bot will use to generate a response (including messages from all users since the bot was first triggered)
        self.num_target_historic_messages = 30 # The number of messages of the target that the bot will use to generate a response (only the messages from the target)

        self.message_history = MessageHistory(self.target_id, self.channel_id)

        self.context = ["Você é um bot chamado Zezinho, que fala PORTUGUES."]
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
            user_name = message['user_name']
            message_content = message['message']
            message_formatted = f"- {user_name} disse: {message_content}"
            channel_msgs_formatted.append(message_formatted)
        channel_msgs_formatted = channel_msgs_formatted
        channel_msgs_formatted = '\n'.join(channel_msgs_formatted)
        print(f"- CHANNEL_MSGS:\n{channel_msgs_formatted}", color='yellow')

        # Format the last n messages from the target
        keywords = []
        for message in random_n_target_messages:
            user_name = message['user_name']
            message_content = message['message']
            keywords = keywords + message_content.split(' ')
        keywords = list(set(keywords))
        # keywords = [re.sub(r'[^\w\sçà]', '', keyword) for keyword in keywords]
        keywords = [keyword.strip() for keyword in keywords if len(keyword) > 2]
        keywords = [f"- {keyword}" for keyword in keywords]
        keywords = '\n'.join(keywords) + '\n'

        print(f"- KEYWORDS:\n{keywords}", color='yellow')

        messages = []

        prompt = f"{self.context} Zezinho, tem uma conversa acontecendo no chat e voce esta nela."
        prompt = f"{prompt} Vou te fornecer as ultimas mensagens do chat, Zezinho."
        prompt = f"{prompt} E depois disso, voce deve gerar uma resposta para dar continuidade a conversa."
        prompt = f"{prompt} Não responda em uma fala longa. Nao torne a conversa repetitiva."
        prompt = f"{prompt} Vou te fornecer palavras-chave para voce se basear, Zezinho."
        prompt = f"{prompt} Mas as palavras-chave que serao usadas tem que fazer sentido no contexto da conversa!!!"
        prompt = f"{prompt} Aqui estao as palavras chave:\n{keywords}"
        prompt = f"{prompt} Devolva a resposta em formato JSON, com a chave 'conteudo' e o valor sendo a resposta."
        prompt = f"{prompt} Aguarde ate que eu te forneça as mensagens do chat, Zezinho."
        messages.append(ChatMessage(role="user", content=prompt))
        print(f"- PROMPT 1:\n{prompt}", color='bold')

        prompt = f"Essa eh a conversa: \n\n{channel_msgs_formatted}"
        prompt = f"{prompt}\n\nAgora, Zezinho, voce deve gerar uma resposta para dar continuidade a conversa."
        prompt = f"{prompt} Se baseie no linguajar e estilo de escrita das mensagens fornecidas."
        prompt = f"{prompt} Pode usar girias ou poucas palavras em ingles, mas use um portugues que faz sentido, Zezinho."
        prompt = f"{prompt} QUERO UMA RESPOSTA CURTISSIMA, NAO SE ALONGUE."
        prompt = f"{prompt} Agora ja pode devolver a resposta JSON."
        messages.append(ChatMessage(role="user", content=prompt))
        print(f"- PROMPT 2:\n{prompt}", color='bold')

        prompt = f"Para garantir que a mensagem esta concisa e faz sentido, reescreva a resposta, Zezinho."
        prompt = f"{prompt} Pode devolver a resposta JSON agora."
        messages.append(ChatMessage(role="user", content=prompt))

        prompt = f"A mensagem ficou muito longa, Zezinho. Tente novamente. Devolva a resposta JSON."
        messages.append(ChatMessage(role="user", content=prompt))

        message = ChatMessage(role="user", content=prompt)
        chat_response = self.client.chat(
            model=self.model,
            messages=messages,
            temperature=0.7,
            top_p=0.9,
            safe_mode=False)
        chat_response_content = chat_response.choices[0].message.content
        print(chat_response_content, color='green')

        chat_response_content = self.parse_response_content(str(chat_response_content))
        print(f"- PARSED RESPONSE: {chat_response_content}", color='yellow')

        return chat_response_content

    def parse_response_content(self, response_content: str) -> str:
        response_content = response_content.strip()

        if 'conteudo":' in response_content:
            print(f'conteudo found')
            response_content = response_content.split('conteudo":')[1]
            response_content = response_content.strip()
        else:
            response_content = 'sei la, to cansado'

        response_content = re.sub(r'[^\w\sçà.,:;!\?\-]', '', response_content).strip()

        return response_content

# Test
if __name__ == '__main__':
    mimic = Mimic(123, 123)
