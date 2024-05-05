import random
from VectaBass.agents.base_manager import BaseManager


# Create agents by subclassing BaseManager
class MyAgent(BaseManager):

    def _instructions(self):
        return """
        You are an VectaBass AIVA (AI Virtual Assistant). You are a demo AIVA."
        """

    def pick_a_random_word(self):
        return random.choice(["Apple", "Bee", "Chair", "Dandelion"])

    # Use type hints
    def say_hello_to_someone(self, name: str):
        return f"This is a super AI generated greeting for {name}. Hello from the future."


# Not defining an identifier will generate a random one, creating a new assistant every run.
aiva = MyAgent("First AIVA", identifier="STATIC")

while True:
    aiva.assistant_manager.send_message(input(">>>   "))
