# Kocom Controller
코콤 월패드의 RS485라인과 연결된 EW11로부터 패킷을 받아 MQTT로 토픽을 발행하는 중계 서버입니다.  
인터넷상의 월패드 컨트롤러들과 호환이 잘 안되어 만들었습니다.  
난방은 집에 구성이 되어있지 않아 추후에 업데이트 하겠습니다.  
# Getting started
Via Docker Compose
```yml
services:
  kocom-controller:
    image: tinylab723/kocom-controller:1.0.0
    restart: unless-stopped
    environment:
      TZ : Asia/Seoul
      LOG_LEVEL: info

      SOCKET_IP: 
      SOCKET_PORT: 
      SOCKET_SYNC_S: 

      MQTT_BROKER: 
      MQTT_PORT: 
      MQTT_BASE_TOPIC: 
      MQTT_USER: 
      MQTT_PASSWORD: 

      ROOM_COUNT: 2

      ROOM_1_ID: 1
      ROOM_1_NAME: living_room
      ROOM_1_LIGHTS: 4
      ROOM_1_HEATER: True

      ROOM_2_ID: 2
      ROOM_2_NAME: kitchen
      ROOM_2_LIGHTS: 2
      ROOM_2_HEATER: True
```

# Configuration
## Overview
| Environment     | Required | Description                                                         |
|-----------------|----------|---------------------------------------------------------------------|
| TZ              | Optional | The timezone for log timestamps.                                    |
| LOG_LEVEL       | Optional | Set log level. Default `info`                                       |
| SOCKET_IP       | Required | IP address of your TCP Client(EW11).                                |
| SOCKET_PORT     | Optional | The TCP port your EW11 device is listening on. Default `8899`.      |
| SOCKET_SYNC_S   | Optional | EW11 synchronization cycle (second). Default `60`.                  |
| MQTT_BROKER     | Required | The IP address of your MQTT broker.                                 |
| MQTT_PORT       | Optional | The port number your MQTT broker is listening on. Default `1883`.   |
| MQTT_BASE_TOPIC | Optional | Base topic to subscribe / publish MQTT messages. Default `kocom`.   |
| MQTT_USER       | Required | MQTT user name.                                                     |
| MQTT_PASSWORD   | Required | MQTT password.                                                      |
| ROOM_COUNT      | Required | The total number of rooms.                                          |
| ROOM_#_ID       | Required | The numeric ID for the room.                                        |
| ROOM_#_NAME     | Required | The name of the room, used in the MQTT topic.                       |
| ROOM_#_LIGHTS   | Required | The number of controllable lights in room.                          |
| ROOM_#_HEATER   | Required | Whether a heater is present in room.                                |


## General
`TZ`  | **Optional**  
The timezone for log timestamps.  
Options : [TZ List](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

`LOG_LEVEL` | **Optional**  
Set log level.  
Shows more detailed logs as the level goes from critical to debug.  
Options : `debug` , `info`, `warning`, `error`, `critical`  
Default : `info` 

## Socket
`SOCKET_IP` | **Required**  
IP address of your TCP Client(EW11).

`SOCKET_PORT` | **Optional**  
The TCP port your EW11 device is listening on.  
Default : `8899`

`SOCKET_SYNC_S` | **Optional**  
EW11 synchronization cycle (second).  
Default : `60`

## MQTT
`MQTT_BROKER` | **Required**  
The IP address of your MQTT broker.

`MQTT_PORT` | **Optional**  
The port number your MQTT broker is listening on.  
Default : `1883`

`MQTT_BASE_TOPIC` | **Optional**  
Base topic to subscribe / publish MQTT messages.  
Default: `kocom`

`MQTT_USER` | **Required**  
MQTT user name.

`MQTT_PASSWORD` | **Required**  
MQTT password.  
Anonymous connection is not supported.

## ROOM
`ROOM_COUNT` | **Required**  
The total number of rooms.  
Controller will only process rooms from `ROOM_1` to `ROOM_{ROOM_COUNT}` no matter how many rooms are configured below.  
MAX : 4

`ROOM_{N}_ID` | **Required**  
The numeric ID for the room.  
This value must be the same as {N}.

`ROOM_#_NAME` | **Required**  
The name of the room, used in th MQTT topic.

`ROOM_{N}_LIGHTS` | **Required**  
The number of controllable lights in room.  
MAX : 8

`ROOM_#_HEATER` | **Required**  
Whether a heater is present in room.  
Options : `True`, `False`

## MQTT Topic 
The controller uses the following topic structure for lights:

* **Command Topic (Subscribe)**: To control a light, publish a message to this topic.
    ```
    <MQTT_BASE_TOPIC>/<ROOM_#_NAME>/light/<light_number>/set
    ```

* **State Topic (Publish)**: The controller publishes the current status of a light to this topic.
    ```
    <MQTT_BASE_TOPIC>/<ROOM_#_NAME>/light/<light_number>/state
    ```

**Placeholders:**
* `<MQTT_BASE_TOPIC>`: The value of your `MQTT_BASE_TOPIC` variable.
* `<ROOM_#_NAME>`: The name of the configured room (e.g., `living_room`).
* `<light_number>`: The index of the light, starting from 1.