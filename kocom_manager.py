import asyncio, logging
from ha_mqtt_client import HaMqttClient
from kocom_tcp_client import KocomTcpClient

class KocomManager:
    def __init__(self, config):
        self.config = config
        self.device_set()
        self.mqtt_client = HaMqttClient(config, self.handle_mqtt_command)
        self.tcp_client = KocomTcpClient(config, self.handle_tcp_command)

    def device_set(self):
        self.device_states = {}
        self.name_to_id = {}
        self.id_to_name = {}
        for room in self.config['rooms']:
            self.device_states[room['name']] = {}
            self.device_states[room['name']]['lights'] = [['Unknown'] for _ in range(room['lights'])]
            self.name_to_id[room['name']] = room['id']
            self.id_to_name[room['id']] = room['name']

            # if room['heater']:
            #     self.device_states[room['name']]['heater'] = ['Unknown']

    async def start(self):
        await self.tcp_client.connect()
        logging.info("Serviece Start!")
        await asyncio.gather(
            self.mqtt_client.handle_messages(),
            self.state_sync()
        )
    
    async def close(self):
        await self.tcp_client.disconnect()
        logging.info("Serviece Stopped")

    async def handle_mqtt_command(self, topic, payload):
        logging.debug(f"Passed MQTT message from module: {topic} -> {payload}")
        mqtt_parts = topic.split('/')
        mqtt_room = mqtt_parts[1]
        mqtt_device = mqtt_parts[2]
        payload = payload.upper()

        if mqtt_room not in self.device_states:
            logging.error(f"Unknown room: {mqtt_room}")
            return            

        if mqtt_device == 'light':
            mqtt_number_light = mqtt_parts[3]
            packet_room =  f"0{self.name_to_id[mqtt_room] - 1} 01 "
            if payload == 'ON':
                packet_number_light = f"00 0{mqtt_number_light} "
                packet_value = ""
                for i in range(8):
                    if i == int(mqtt_number_light) - 1:
                        packet_value += "FF "
                    else:
                        packet_value += "00 "

            else: #payload == 'OFF'
                packet_number_light = f"00 0{mqtt_number_light} "
                packet_value = f"00 00 00 00 00 00 00 00 "

            packet = f"30 BC 00 0E {packet_room}{packet_number_light}{packet_value}"

            temp_p = packet.split()
            temp = 0
            for i in temp_p:
                temp += int(i, 16)
            check_sum = f"{temp % 256:X}"

            packet = f"AA 55 {packet}{check_sum} 0D 0D"
        
        # elif mqtt_device == 'heater':
        #     packet = ""

        await self.tcp_client.send_packet(packet)
        logging.debug(f"Pass TCP packet to module: {packet}")
        await self.mqtt_client.publish_state(topic[:-4] + '/state', payload)

    async def handle_tcp_command(self, packet):
        logging.debug(f"Passed TCP packet from module: {packet}")
        room_name = self.id_to_name[int(packet[9]) + 1]
        device_type = 'light' if packet[14:16] else 'heater'
        states = packet[20:36]

        changed = 0
        if device_type == 'light':
            for i in range(len(self.device_states[room_name]['lights'])):
                state = 'ON' if states[i * 2 : i * 2 + 2] == 'FF' else 'OFF'

                if state != self.device_states[room_name]['lights'][i]:
                    await self.mqtt_client.publish_state(f"kocom/{room_name}/light/{i + 1}/state", state)
                    self.device_states[room_name]['lights'][i] = state
                    changed += 1

        # elif device_type == 'heater':
        #     pass

        logging.info("Nothing changed")

    async def state_sync(self):
        while True:
            await self.tcp_client.tcp_state_sync()
            await asyncio.sleep(self.config['socket']['sync_s'])


