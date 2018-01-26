import yaml
import sys
import time
from network import Network

class Janus:
    global_config_file = "global"
    config_dir = "/config/"
    config_file_extention = ".yaml"

    def __init__(self):
        self.global_config = None
        try:
            with open(self.config_dir + self.global_config_file + self.config_file_extention) as fp:
                self.global_config = yaml.load(fp)

        except IOError:
            print("Error loading configuration files.")
            return

        self.network = Network(self.global_config)

    def tick(self):
        self.network.predict()

    def stop(self):
        pass

if __name__ == "__main__":
    janus = Janus()
    starttime=time.time()
    try:
        while True:
            janus.tick()
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))
    except KeyboardInterrupt:
        janus.stop()