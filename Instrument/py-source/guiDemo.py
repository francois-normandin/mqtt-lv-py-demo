import PySimpleGUI as psg
from datetime import datetime, timedelta
from mqttClient import mqttClientDemo
from time import sleep
import json
import threading

def run_demo_gui():
    #Variables
    client1 = mqttClientDemo(brokerUrl=r'localhost', brokerPort = 1883)
    setpointTopic = r'system/setpoint'
    enableTopic = r'systen/enable'
    targetTopic = r'system/target'

    #Request methods
    def sendSetpointCommand(topic = setpointTopic, setpoint = 25.0):
        if client1.isConnected == False:
            return 'not connected'
        # send command
        targetRequest = {"setpoint": setpoint}
        client1.publish(topic, json.dumps(targetRequest))
        return 'MQTT command return'

    def sendEnableCommand(topic = enableTopic, enabled = False):
        if client1.isConnected == False:
            return 'not connected'
        # send command
        targetRequest = {"enabled": enabled}
        client1.publish(topic, json.dumps(targetRequest))
        return 'MQTT command return'

    def sendTargetCommand(topic = targetTopic, enabled = False, setpoint = 25.0):
        if client1.isConnected == False:
            return 'not connected'
        # send command
        targetRequest = {"enabled": enabled, "setpoint": setpoint, "responseURI": (client1.clientName + '/target-command')}
        client1.publish(topic, json.dumps(targetRequest))
        return 'MQTT command return'

    def pcrCycle(denaturation=95.0, annealing=55.0, elongation=72.0, dwelltime=5):
        elapsed = 0
        cycleFinished = False
        while not cycleFinished:
            if elapsed == 0:
                sendTargetCommand(targetTopic, True, denaturation)
                publishPcrState("denaturation")
            elif elapsed == dwelltime:
                sendTargetCommand(targetTopic, True, annealing)
                publishPcrState("annealing")
            elif elapsed == (2*dwelltime):
                sendTargetCommand(targetTopic, True, elongation)
                publishPcrState("elongation")
            elif elapsed == (3*dwelltime):
                cycleFinished = True
            sleep(1)
            elapsed += 1
        
    def publishPcrState(step = 'unknown', cycle = None):
        state = {"step": step}
        if cycle != None:
            state["loop"] = cycle
        client1.publish(client1.clientName + r'/state', json.dumps(state))
        return json.dumps(state)

    def executepcrCycle(mqttClient, nbCycles):
        if nbCycles == 0:
            return

        disconnectOnComplete = False
        if client1.isConnected == False:
            client1.connect()
            disconnectOnComplete = True

        publishPcrState("Starting PCR Cycling")
        sendTargetCommand(targetTopic, True, 95.0)
        sleep(5)
        for i in range(nbCycles):
            publishPcrState("PCR Cycle", i+1)
            pcrCycle()

        publishPcrState("PCR Cycling Complete")
        sendTargetCommand(targetTopic, False)
        if disconnectOnComplete:
            client1.disconnect()
        

    autoTab = [
                [psg.T('Call a script in Python which automates some actions.')],
                [psg.Text(' ')],
                [psg.Text('Number of cycles'), psg.InputText('5', size=(5,1), key='-nbCycles-', enable_events=True)],
                [psg.Button('Run PCR Cycle script', size=(20,2), key='-callPcr-')]
            ]
    manualTab = [
                    [psg.T('Manual control')],
                    [psg.Text(' ')],
                    [psg.Text('Hostname'), psg.InputText('localhost', size=(35,1), key='-hostname-', enable_events=False)],
                    [psg.Button('Connect', size=(20,2), visible=True, key='-connect-')],
                    [psg.Checkbox('Enable command', size=(12, 1), default=False, visible=False, enable_events=True, key='-cmdEnable-')],
                    [   
                        psg.Text(   'Set point:',
                                    size=(8, 1), 
                                    visible=False, 
                                    key='-tempText-'
                                ), 
                        psg.Slider  ( 
                                        range=(0.0,120.0),
                                        default_value=25.0, 
                                        size=(20,15), 
                                        orientation='horizontal', 
                                        font=('Helvetica', 12), 
                                        visible=False, 
                                        key='-tempInput-', 
                                        enable_events=True
                                    )
                    ]
                ]

    layout = [  [psg.TabGroup(
                    [   [psg.Tab('Manual', manualTab), 
                        psg.Tab('Async script', autoTab)]])],
                [psg.Text('Response', size=(20,1))],
                [psg.Text('', size=(40,1), key='-response-')]]

    window = psg.Window('MQTT Python Client (View)', layout, finalize=True)

    while True:

        event, values = window.read()
        if event == '-connect-':
            if client1.isConnected:
                client1.disconnect()
                window[event].update('Connect')
                window['-cmdEnable-'].update(visible = False)
                window['-tempInput-'].update(visible = False)
                window['-tempText-'].update(visible = False)
            else:
                client1.brokerUrl = values['-hostname-']
                client1.connect()
                window['-connect-'].update('Disconnect')
                window['-cmdEnable-'].update(visible = True)
                window['-tempInput-'].update(visible = True)
                window['-tempText-'].update(visible = True)
            

        elif event == '-callPcr-':
            t = threading.Thread(target=executepcrCycle, args=(client1, int(values['-nbCycles-'])))
            t.start()

        elif event == '-cmdEnable-':
            slider = window['-tempInput-']
            targetSetpoint = slider.TKScale.get()
            targetEnabled = bool(window['-cmdEnable-'].get())
            sendTargetCommand(targetTopic, targetEnabled, targetSetpoint)

        elif event == '-tempInput-':
            slider = window['-tempInput-']
            targetSetpoint = slider.TKScale.get()
            targetEnabled = bool(window['-cmdEnable-'].get())
            sendTargetCommand(targetTopic, targetEnabled, targetSetpoint)

        elif event == psg.WIN_CLOSED:           # always,  always give a way out!
            break

    return "program stopped"