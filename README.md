# VectaBass Agents Framework
## About This Package
VectaBass is dedicated to bringing AI Virtual Assistants (AIVAs) into everyday life by providing an open-source platform for autonomous AI Agent creation. Our approach is object-oriented, empowering developers to define AI agents through Python classes.

VectaBass not only aims to facilitate the building of individual Agents but also orchestrates interactions between groups of Agents, known as Swarms. This framework is designed to be flexible and extensible, making it ideal for both personal and professional applications in creating dynamic and interactive AI solutions.

## Installation and Setup
Install VectaBass to start creating your own AI agents:

```bash
pip install -r requirements.txt
```

### Remember to set your OpenAI API key
Follow the instructions here: https://platform.openai.com/docs/quickstart.

## Quick Start
Below is a simple example demonstrating how to create an AI agent using the VectaBass framework:


```python
import random
from VectaBass.agents.base_manager import BaseManager

# Create agents by subclassing BaseManager
class MyAgent(BaseManager):

    def _instructions(self):
        return """
        You are an VectaBass AIVA (AI Virtual Assistant). You are a demo AIVA.
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
```
## Features
- Object-Oriented AI Agents: Define your AI assistants through Python classes.
- Swarm Interactions: Manage interactions between multiple agents, enhancing the complexity and capability of your AI solutions.
- Seamless Integration: Easy integration with other Python libraries and existing infrastructure.

## Contributing
We welcome contributions from the community. Whether you're fixing a bug, adding a feature, or improving the documentation, your help is appreciated!

- Fork the Project
- Create your Feature Branch (git checkout -b feature/AmazingFeature)
- Commit your Changes (git commit -m 'Add some AmazingFeature')
- Push to the Branch (git push origin feature/AmazingFeature)
- Open a Pull Request

## License
Distributed under the MIT License. See LICENSE for more information.

## Contact
Your Name - @YourTwitter - email

- Project Link: [https://github.com/yourusername/vectabass](https://github.com/OWigginsHay/VectaBass)
- Website Link: https://www.vectabass.com

