import asyncio, logging

class KocomTcpClient:
    def __init__(self, config, handle_tcp_command):
        self.config = config
        self.handle_tcp_command = handle_tcp_command

    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.config['socket']['ip'], self.config['socket']['port'])
            logging.info('TCP Socket Connected!')
        except Exception as e:
            logging.warning(e)

    async def disconnect(self):
        try:
            if not self.writer:
                return
            if not self.writer.is_closing():
                self.writer.close()
            await self.writer.wait_closed()
        except Exception as e:
            logging.warning(e)
        
    async def send_packet(self, packet):
        logging.debug(f"Passed TCP packet from module: {packet}")
        try:
            self.writer.write(bytes.fromhex(packet.replace(" ", "")))
            await self.writer.drain()
            logging.info(f"Transmitted TCP packet: {packet}")
        except Exception as e:
            logging.warning(e)

    async def tcp_state_sync(self):
        try:
            await self.send_packet("AA 55 30 9C 00 0E 00 01 00 3A 00 00 00 00 00 00 00 00 15 0D 0D")
            packet = await self.reader.read(1024)
        except Exception as e:
            logging.warning(e)
        
        if not packet:
            raise Exception("TCP Connection lost")
        
        packet = packet.split(b'\r\r')
        message = -1
        for i in packet:
            if i.hex().upper()[:8] == 'AA5530BC':
                message = i.hex().upper()

        if message == -1:
            logging.error("Failed to recieve sync data")
            return
        else:
            logging.info(f"Recieved TCP packet:    {message}")
            await self.handle_tcp_command(message)