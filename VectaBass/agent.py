from .chat_strategy import Chat, OpenAIStrategy
from .pub_sub_manager import PubSub


class Agent:

    def __init__(self, parent) -> None:
        self.parent = parent
        self.chat = Chat(OpenAIStrategy(parent))
        self.pubsub = PubSub()
        self.pubsub.subscribe(f"print_message_{self.parent.name}", self.print_message)

    def send_message(self, message):
        self.chat.send_message(message)

    def print_message(self, message):
        print(self)
        print(message)
