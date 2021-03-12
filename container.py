import json
import os.path as path

Config: dict = {
    'gui': {
        'window': {
            'pos': [10, 10]
        }
    },
    'observer': {
        'zone': [20,777,550,1028]
    },
    'sid': ''
}


class Container:
    
    configPath = 'config.json'
    
    def __init__(self):
        mode = 'w+'
        if path.exists(self.configPath):
            mode = 'r'
        with open(self.configPath, mode) as file:
            self.loadConfigFromFile(file)
    
    def config(self) -> Config:
        return self.config

    def loadConfigFromFile(self, file):
        self.config: Config
        self.configFile = file
        try:
            self.config = json.load(file)
        except json.JSONDecodeError:
            self.config = Config

    def saveConfig(self):
        with open(self.configPath, 'w') as file:
            json.dump(self.config, file)
