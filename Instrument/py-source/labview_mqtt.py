
from mqttClient import mqttClientDemo
from urllib.parse import urlparse
import json
from time import sleep
import threading
from guiDemo import run_demo_gui

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

def run():
    t = threading.Thread(target=run_demo_gui, args=())
    t.start()
    #run_demo_gui()
    return "program launched asynchronously"

def mqttRunCycle(testName = 'testClientName', hosturl = r'localhost', nb_loop = 10):
    request = {"enabled": False, "setpoint": 25.0}
    info = {"step": "PCR Cycling"}
    client2 = mqttClientDemo(brokerUrl = hosturl, brokerPort = 1883)

    def cfg_and_send(enabled = None, setpoint = None, message = None):
        if enabled != None:
            request["enabled"] = enabled
        if setpoint != None:
            request["setpoint"] = setpoint
        if message != None:
            info["step"] = message
        
        # publish request and info statement    
        client2.publish(command_topic, json.dumps(request))
        client2.publish(client2.clientName + r'/state', json.dumps(info))
        return

    # Connect to instrument
    client2.connect()
    cfg_and_send(False, 25.0, "connected to instrument")
    sleep(1)
    
    # Initial Denaturation Step
    cfg_and_send(True, 95.0, "initial denaturation")
    sleep(10)

    # PCR Cycles
    i = list(range(1, nb_loop+1))
    for x in i:
        cfg_and_send(setpoint = 95.0, message = "denaturation")
        sleep(3)

        cfg_and_send(setpoint = 55.0, message = "annealing")
        sleep(3)

        cfg_and_send(setpoint = 72.0, message = "elongation")
        sleep(5)

    # Final Elogation Step
    cfg_and_send(message = "final elongation")
    sleep(10)
    
    # Disable
    cfg_and_send(False, 25.0, "PCR complete")
    sleep(1)

    # Disconnect
    cfg_and_send(message = "disconnecting from instrument")
    client2.disconnect()
    return 'cycle complete'

def mqttDisconnect():
    if len(mqttSession) > 0:
        client1 = mqttSession[0]
        client1.disconnect()   
        return 'MQTT Session disconnected'
    else: 
        return 'no MQTT Session found'



