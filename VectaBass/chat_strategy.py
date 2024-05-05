from abc import ABC, abstractmethod
import json
import time
from openai import OpenAI
from pydantic import BaseModel
from .pub_sub_manager import PubSub
from openai._types import NotGiven


class ChatStrategy(ABC):

    @abstractmethod
    def send_message(self, message, thread_id) -> str:
        pass

    @abstractmethod
    def add_tool(self, config, tools_to_remove):
        pass

    @abstractmethod
    def get_thread(self):
        pass

    @abstractmethod
    def set_thread(self, thread):
        pass

    @abstractmethod
    def add_message_to_thread(self, thread_id, message, role="user"):
        pass


class OpenAIStrategy(ChatStrategy):

    def __init__(self, parent) -> None:
        self.client = OpenAI()
        self.thread = None
        self.assistant = None
        self.manager = parent
        self.pubsub = PubSub()
        self.message_queue = []
        self.is_processing = False
        self.init_chat()
        super().__init__()

    def init_chat(self):
        self.thread = self.create_thread()
        self.assistant = self.get_assistant(assistant_name=self.manager.name)

    def add_message_to_thread(self, thread_id, message, role="user"):
        message = self.client.beta.threads.messages.create(thread_id=thread_id, role=role, content=message)

    def create_thread(self):
        thread = self.client.beta.threads.create()
        return thread

    def get_thread(self):
        return self.thread

    def set_thread(self, thread):
        self.thread = thread

    def start_chat(self):
        main_thread = self.create_thread()
        self.thread = main_thread
        self.add_message_to_thread(main_thread.id, "How can I help you?", role="assistant")
        return self.client.beta.threads.retrieve(main_thread.id)

    def send_message(self, message, direct=False):
        self.message_queue.append((message, direct))
        if not self.is_processing:
            self.process_message_queue()

    def process_message_queue(self):
        if not self.message_queue:
            self.is_processing = False
            return

        message, direct = self.message_queue.pop(0)
        self.is_processing = True

        self.add_message_to_thread(self.thread.id, message)
        if direct is False:
            tools = self.assistant.tools
        else:
            tools = {}
        run = self.client.beta.threads.runs.create(thread_id=self.thread.id, assistant_id=self.assistant.id, tools=tools)
        self.wait_for_completion(self.thread.id, run.id)

    def add_tool(self, config, tools_to_remove=[]):
        print("adding tool")
        self.assistant = self.get_assistant(assistant_name=self.manager.name, tool_schema=config, tools_to_remove=tools_to_remove)

    def get_assistant(self, assistant_name="tester_app", tool_schema=NotGiven(), tools_to_remove=[]):
        try:
            # List all assistants
            assistants = self.client.beta.assistants.list()
            for assistant in assistants.data:
                if assistant.name == assistant_name:
                    new_tools = getattr(assistant, "tools", [])

                    # Only merge if a new tool schema has been provided
                    if not isinstance(tool_schema, NotGiven):
                        new_tools = self.merge_tools(new_tools, tool_schema, tools_to_remove=tools_to_remove)

                    print(f"Found existing assistant: {assistant_name}")
                    assistant = self.client.beta.assistants.update(
                        assistant_id=assistant.id,
                        description=str(assistant.description),
                        instructions=self.manager._instructions(),
                        model=assistant.model,
                        tools=new_tools,
                    )
                    return assistant

            # If no existing assistant found, create a new one
            print(f"Creating new assistant: {assistant_name}")
            new_assistant = self.client.beta.assistants.create(
                name=assistant_name,
                instructions="You are a virtual assistant. Use the provided functions to handle queries.",
                model="gpt-3.5-turbo",
                tools=tool_schema,
            )
            return new_assistant

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def merge_tools(self, existing_tools, new_tool_schema, tools_to_remove=[]):
        # Transform existing tools into a dictionary for easier lookup
        existing_tools_dict = {tool.function.name: tool for tool in existing_tools}
        for tool_name in tools_to_remove:
            if tool_name in existing_tools_dict:
                del existing_tools_dict[tool_name]
        # Iterate through new tools and merge or add appropriately
        for new_tool in new_tool_schema:
            tool_name = new_tool["function"]["name"]
            if tool_name in existing_tools_dict:
                # If marked for removal, skip updating and schedule for deletion
                if tool_name in tools_to_remove:
                    continue
                # Update the existing tool with new tool information
                existing_tools_dict[tool_name] = new_tool
            elif tool_name not in tools_to_remove:
                # Add new tool if it's not marked for removal
                existing_tools_dict[tool_name] = new_tool

        # Remove the tools as specified by tools_to_remove
        for tool_name in tools_to_remove:
            if tool_name in existing_tools_dict:
                del existing_tools_dict[tool_name]

        # Convert the dictionary back to a list for the final merged tools
        return list(existing_tools_dict.values())

    def process_tool_calls(self, required_action):
        tool_outputs = []

        for tool_call in required_action.submit_tool_outputs.tool_calls:
            func_identifier = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            method_details = self.manager.registry.methods.get(func_identifier)
            print(func_identifier)
            print(arguments)
            if not method_details:
                # If not found, try the model-specific methods registry
                method_details = self.manager.registry.model_methods.get(func_identifier)
                if not method_details:
                    output = {"error": f"Method identifier {func_identifier} not found in any registry."}
                    # print(output)
                    tool_outputs.append({"tool_call_id": tool_call.id, "output": str(output)})
                    continue

            manager = method_details.method.__self__
            method_name = method_details.method.__name__
            self.pubsub.publish(f"system_function_call", method_name)
            parameter_models = method_details.annotations

            try:
                method_args = {}
                for arg_name, arg_value in arguments.items():
                    model_class = parameter_models.get(arg_name)
                    if model_class and issubclass(model_class, BaseModel):
                        instance = model_class(**arg_value)
                        method_args[arg_name] = instance
                        print(f"Instantiated {arg_name}: {instance}")
                    else:
                        method_args[arg_name] = arg_value

                # print(f"Method arguments: {method_args}")
                method = getattr(manager, method_name, None)
                if method:
                    result = method(**method_args)
                    output = {"result": result}
                else:
                    output = {"error": f"Method {method_name} not found on the manager {manager.identifier}."}

            except Exception as e:
                output = {"error": str(e)}
                print(f"Error processing {func_identifier}: {e}")

            # print(output)
            tool_outputs.append({"tool_call_id": tool_call.id, "output": str(output)})

        return tool_outputs

    def wait_for_completion(self, thread_id, run_id, max_retries=3, retry_delay=1):
        retry_count = 0
        while retry_count < max_retries:
            run = self.client.beta.threads.runs.retrieve(run_id=run_id, thread_id=thread_id)
            while run.status != "completed":
                run = self.client.beta.threads.runs.retrieve(run_id=run_id, thread_id=thread_id)
                if run.status == "requires_action":
                    outputs = self.process_tool_calls(run.required_action)
                    run = self.client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run.id, tool_outputs=outputs)
                elif run.status in ["in_progress", "queued"]:
                    time.sleep(1)
                elif run.status == "failed":
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"Run failed. Retrying ({retry_count}/{max_retries})...")
                        time.sleep(retry_delay)
                        break
                    else:
                        print("Max retries reached. Aborting.")
                        return
                else:
                    print(run.status)
                    break

            if run.status == "completed":
                break

        self.print_responses(thread_id=thread_id)
        self.process_message_queue()

    def print_responses(self, thread_id) -> str:
        messages = self.client.beta.threads.messages.list(thread_id)
        message = messages.data[0].content[0].text.value
        self.pubsub.publish(f"print_message_{self.manager.name}", f"**{self.manager.name}**" + ": \n" + message)


class Chat:
    def __init__(self, strategy: ChatStrategy) -> None:
        self.strategy = strategy

    def send_message(self, message, direct=False):
        return self.strategy.send_message(message, direct)

    def add_tool(self, config, tools_to_remove):
        self.strategy.add_tool(config, tools_to_remove)

    def init_chat(self):
        self.strategy.init_chat()

    def get_thread(self):
        return self.strategy.get_thread()

    def set_thread(self, thread):
        self.strategy.set_thread(thread)

    def add_message(self, thread, message):
        self.strategy.add_message_to_thread(thread.id, message=message)
