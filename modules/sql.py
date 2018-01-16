import sqlite3

class SqlHelper:
    def __init__(self, global_config, currency_config):
        self.global_config = global_config
        self.currency_config = currency_config

        conn = sqlite3.connect(global_config["database_dir"] + currency_config["name"] + ".db")
        c = conn.cursor()
        try:
            fp = open('config/setup.sql')
            line = fp.readline()
            while line:
                try:
                    c.execute(line)
                except sqlite3.OperationalError:
                    pass
                finally:
                    line = fp.readline()
        finally:  
            fp.close()
        conn.close()

    def get(self):
        return sqlite3.connect(self.global_config["database_dir"] + self.currency_config["name"] + ".db")