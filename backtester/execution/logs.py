class create:
    def __init__(self):
        self.balance_history = []
        self.error_msg = {}
        self.open_pos_msg = {}
        self.close_pos_msg = {}

    def add_error_msg(self, date, msg):
        self.error_msg[date] = msg

    def add_open_msg(self, date, msg, option_names):
        self.open_pos_msg[date] = [msg, option_names]

    def add_close_msg(self, date, msg, option_names):
        self.close_pos_msg[date] = [msg, option_names]
