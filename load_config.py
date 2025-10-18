import re, logging, os

class LoadConfig:
    def __init__(self):
        self.config = self._load()

    def _load(self):
        config = {
            'socket': {},
            'mqtt': {},
            'rooms': [],
            'log_level': ''
        }
        log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }

        config['log_level'] = os.getenv('LOG_LEVEL', 'info').upper()
        logging.basicConfig(level=log_levels[config['log_level']], format='%(asctime)s %(levelname)s [%(module)s] %(message)s')

        ip_pattern = re.compile(
        r"^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\."
        r"(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\."
        r"(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\."
        r"(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$"
        )
        config['socket']['ip'] = os.getenv('SOCKET_IP')
        config['socket']['port'] = int(os.getenv('SOCKET_PORT', 8899))
        config['socket']['sync_s'] = int(os.getenv('SOCKET_SYNC_S', 60))
        if not ip_pattern.match(config["socket"]["ip"]):
            logging.error("Invalid Socket IP format. ")
            return None

        config['mqtt']['broker'] = os.getenv('MQTT_BROKER')
        config['mqtt']['port'] = int(os.getenv('MQTT_PORT', 1883))
        config['mqtt']['base_topic'] = os.getenv('MQTT_BASE_TOPIC', 'kocom')
        config['mqtt']['user'] = os.getenv('MQTT_USER')
        config['mqtt']['password'] = os.getenv('MQTT_PASSWORD')
        if not ip_pattern.match(config["mqtt"]["broker"]):
            logging.error("Invalid MQTT IP format. ")
            return None
        
        room_index = int(os.getenv('ROOM_COUNT'))

        for i in range(room_index):
            config['rooms'].append({
                'id' : int(os.getenv(f"ROOM_{i + 1}_ID")), 
                'name': os.getenv(f'ROOM_{i + 1}_NAME'),
                'lights': int(os.getenv(f'ROOM_{i + 1}_LIGHTS')),
                'heater': os.getenv(f'ROOM_{room_index}_HEATER', 'False').lower() == 'true'
                })

        return config
        
    def load(self):
        if self.config:
            logging.info("Successfully loaded condig file.")
            return self.config
        
        else:
            logging.error("Failed to load config")
            exit()
