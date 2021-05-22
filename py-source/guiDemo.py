import PySimpleGUI as psg
from datetime import datetime, timedelta
from mqttClient import mqttClientDemo
from time import sleep
import threading

def sendTemperatureSetpoint(mqttClient, topic, strSetpoint):
    if mqttClient.isConnected == False:
        return
    # send command
    return 'mqTT command return'

def psrCycle(mqttClient, cycleLowTemp=45, cycleLowSecs=10, cycleHighTemp=75, cycleHighSecs=10, endtemp=25):
    if mqttClient.isConnected == False:
        mqttClient.connect()

    elapsed = 0
    cycleFinished = False
    while not cycleFinished:
        if elapsed == 0:
            pass # send mqtt message to set low cycle temperature
        elif elapsed == cycleLowSecs:
            pass # send mqtt message to set high cycle temperature
        elif elapsed >= (cycleLowSecs + cycleHighSecs):
            pass # send mqtt message to set end cycle temperature
            cycleFinished = True
        sleep(1)
        elapsed += 1

def executePSRCycle(mqttClient, nbCycles):
    if nbCycles == 0:
        return

    for i in range(nbCycles):
        psrCycle(mqttClient)

autoTab = [[psg.T('Call a script in Python which automates some actions.')],
           [psg.Text(' ')],
           [psg.Text('Number of cycles'), psg.InputText('0', size=(5,1), key='-nbCycles-', enable_events=True)],
           [psg.Button('Call PSR Cycle script', size=(20,2), key='-callPsr-')]]
manualTab = [[psg.T('Manually control temperature set-point')],
             [psg.Text(' ')],
             [psg.Button('Connect', size=(20,2), key='-connect-')],
             [psg.Checkbox('Enable commands', size=(12, 1), default=False, enable_events=True, key='-cmdEnable-')],
             [psg.Text('Temp. set point (degC):', size=(18, 1), key='-tempText-'), psg.InputText('25', size=(6,1), visible=False, key='-tempInput-', enable_events=True)],
             [psg.Button('Submit', size=(1,1), visible=False, bind_return_key=True)]]

layout = [[psg.TabGroup([[psg.Tab('Manual', manualTab), psg.Tab('Script-based', autoTab)]])], [psg.Text('Response', size=(20,1))], [psg.Text('', size=(40,1), key='-response-')]]
window = psg.Window('My window with tabs', layout, finalize=True)

client1 = mqttClientDemo()
tempSetpointTopic = 'whatever'

lastAcceptedTempString = None
entryAcceptTimeout = None
while True:

    if entryAcceptTimeout is not None:
        delta = datetime.now() - entryAcceptTimeout
        if delta.total_seconds() >= 0:
            lastAcceptedTempString = window['-tempInput-'].get()
            entryAcceptTimeout = None
            window['-response-'].update(sendTemperatureSetpoint(client1, tempSetpointTopic, lastAcceptedTempString))

    event, values = window.read()
    if event == '-connect-':
        client1.connect()

    elif event == '-callPsr-':
        t = threading.Thread(target=executePSRCycle, args=(client1, int(values['-nbCycles-'])))
        t.start()

    elif event == '-cmdEnable-':
        #window['-tempText-'].update(visible=values['-cmdEnable-'])
        window['-tempInput-'].update(visible=values['-cmdEnable-'])

    elif event == '-tempInput-':
        if len(values['-tempInput-']) and values['-tempInput-'][-1] not in ('0123456789.'):
            window['-tempInput-'].update(values['-tempInput-'][:-1])    # delete last char from input
        else:
            entryAcceptTimeout = datetime.now() + timedelta(seconds=1)
    elif event == '-nbCycles-':
        if len(values['-nbCycles-']) and values['-nbCycles-'][-1] not in ('0123456789'):
                window['-nbCycles-'].update(values['-nbCycles-'][:-1])  # delete last char from input

    elif event == 'Submit':
        lastAcceptedTempString = window['-tempInput-'].get()
        entryAcceptTimeout = None
        window['-response-'].update(sendTemperatureSetpoint(client1, tempSetpointTopic, lastAcceptedTempString))

    elif event == psg.WIN_CLOSED:           # always,  always give a way out!
        break
