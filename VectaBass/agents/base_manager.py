# base_manager.py
import uuid
from ..registry import Registry, ManagerRegistry
from ..agent import Agent

import logging

# Set up logging
logging.basicConfig(
    filename="system_log.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class BaseManager:
    def __init__(self, name: str, identifier=None):
        self.identifier = identifier or uuid.uuid4().hex
        self.name = f"{name}_{self.identifier}"
        self.assistant_manager = Agent(self)
        self.registry = Registry(self)
        ManagerRegistry.add_manager(self)

    def _instructions(self):
        return ""

    def __call__(self, method_name: str, *args, **kwargs):
        method = getattr(self, method_name, None)
        if callable(method):
            return method(*args, **kwargs)
        raise AttributeError(f"Method {method_name} not found in {self.__class__.__name__}")

    # def send_message_to_agent(self, agent_name: str, message: str):
    #     """This is the only way to talk directly with an agent that is not the project manager. Use the agents system name and include the message you wish to send"""
    #     manager = ManagerRegistry.managers.get(agent_name, None)
    #     if manager:
    #         manager.assistant_manager.chat.send_message(
    #             f"message from {self.name}"
    #             + ": "
    #             + message
    #             + " >> Reply to this agent if you have important data to respond with only. Respond using the send_message tool, direct outputs are not read by the sending agent."
    #         )
    #     else:
    #         return f"Manager not found, must be one of: {ManagerRegistry.managers.keys()}"

    # def get_list_of_agents(self):
    #     """Returns the names of all available agents to message"""
    #     return ManagerRegistry.managers.keys()
