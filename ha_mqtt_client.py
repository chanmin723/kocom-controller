import aiomqtt, logging, time
class HaMqttClient:
    def __init__(self, config, handle_mqtt_command):
        self.config = config
        self.handle_mqtt_command = handle_mqtt_command
        self.client = aiomqtt.Client(
            hostname = self.config['mqtt']['broker'],
            port = self.config['mqtt']['port'],
            username = self.config['mqtt']['user'],
            password =self.config['mqtt']['password']
        )
        
    async def handle_messages(self):
        try:
            async with self.client as client:
                await self.client.subscribe("kocom/#")
                async for message in client.messages:
                    topic = str(message.topic)
                    payload = message.payload.decode() # type: ignore
                    if topic.endswith("/set"):
                        logging.info(f"Received message on {topic}: {payload}")
                        await self.handle_mqtt_command(topic, payload)
                        time.sleep(0.2)
        except Exception as e:
            logging.warning(e)
                
    async def publish_state(self, topic, payload):
        logging.debug(f"Passed MQTT message from module: {topic} -> {payload}")
        try:
            await self.client.publish(topic, payload)
            logging.info(f"Published message on {topic}: {payload}")
        except Exception as e:
            logging.warning(e)