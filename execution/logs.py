import execution

class logs:
    def __init__(self):
        self.balance_history = []
        self.error_messages = {}

    def add_error_msg(date, msg):
        self.error_messages[date] = msg
