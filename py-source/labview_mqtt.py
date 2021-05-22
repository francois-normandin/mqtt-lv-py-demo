
from mqttClient import mqttClientDemo
from urllib.parse import urlparse
from time import sleep

command_topic = r'system/target'
state_topic = r'system/state'

# LabVIEW cannot call directly a class method, so calls must be abstracted in a module (.py)

'Using a list to store the object persistently during the LabVIEW-Python session'
mqttSession = []

def mqttConnect(client_name, host_uri):
    hostURI = urlparse(host_uri) 
    if len(mqttSession) == 0:
        client1 = mqttClientDemo(clientName=client_name, brokerUrl = host_uri)
        mqttSession.append(client1)
        client1.connect()
    else: 
        client1 = mqttSession[0]
    return client1.clientName

def mqttPublish(topic = command_topic, payload = '{"setpoint": 25.0, "enable": false}'):
    if len(mqttSession) > 0:
        client1 = mqttSession[0]
        client1.publish(topic, payload)
        return client1.clientName
    else: 
        return 'no MQTT Session found'

def mqttSubscribe(topic = state_topic):
    if len(mqttSession) > 0:
        client1 = mqttSession[0]
        client1.subscribe(topic)
        return client1.clientName
    else: 
        return 'no MQTT Session found'

def mqttUnsubscribe(topic = state_topic):
    if len(mqttSession) > 0:
        client1 = mqttSession[0]
        client1.unsubscribe(topic)
        return client1.clientName
    else: 
        return 'no MQTT Session found'

def mqttRunCycle(testName = 'testClientName', hosturl = r'localhost', nb_loop = 10):
    client2 = mqttClientDemo(brokerUrl = hosturl, brokerPort = 1883)
    client2.connect()
    sleep(1)
    client2.publish(command_topic, '{"setpoint": 95.0, "enable": true}')
    client2.publish(client2.clientName + r'/state', '{"step": "initial denaturation", "loop": 0}')
    sleep(10)
    i = list(range(1, nb_loop+1))
    for x in i:
        client2.publish(command_topic, '{"setpoint": 95.0, "enable": true}')
        client2.publish(client2.clientName + r'/state', '{"step": "denaturation", "loop": ' + str(x) + '}')
        sleep(3)
        client2.publish(command_topic, '{"setpoint": 55.0, "enable": true}')
        client2.publish(client2.clientName + r'/state', '{"step": "annealing", "loop": ' + str(x) + '}')
        sleep(3)
        client2.publish(command_topic, '{"setpoint": 72.0, "enable": true}')
        client2.publish(client2.clientName + r'/state', '{"step": "elongation", "loop": ' + str(x) + '}')
        sleep(5)
    client2.publish(command_topic, '{"setpoint": 72.0, "enable": true}')
    client2.publish(client2.clientName + r'/state', '{"step": "final elongation", "loop": ' + str(x) + '}')
    sleep(10)
    client2.publish(command_topic, '{"setpoint": 25.0, "enable": false}')
    sleep(1)
    client2.disconnect()
    return 'cycle complete'

def mqttDisconnect():
    if len(mqttSession) > 0:
        client1 = mqttSession[0]
        client1.disconnect()
        
        return 'MQTT Session disconnected'
    else: 
        return 'no MQTT Session found'



