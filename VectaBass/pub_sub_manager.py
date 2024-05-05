class PubSub:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PubSub, cls).__new__(cls)
            # Initialize any variables here
            cls._instance.subscribers = {}
        return cls._instance

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def unsubscribe(self, event_type, callback):
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)

    def publish(self, event_type, data):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(data)
