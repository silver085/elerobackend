class MessageCounterTable:

    def __init__(self):
        self.table = {}

    def get_counter(self, remote_id):
        s_remote_id = str(remote_id)
        try:
            self.table[s_remote_id] += 1 & 0xFF
        except Exception as e:
            self.table[s_remote_id] = 1 & 0xFF

        return self.table[s_remote_id]

    def dump_table(self):
        for obj in self.table:
            print(f"Object in table: {obj}")
