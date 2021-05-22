import paho.mqtt.client as mqtt
import requests
import logging
from random import randint

_LOG_FILE_NAME = 'mqttClientDemo_log.txt'

def url_ok(url):
    r = requests.head(url)
    return r.status_code == 200

class mqttClientDemo(object):

    def __init__(self, **kwargs):
        self.clientName = kwargs.get('clientName', 'Client'+str(randint(0, 8191)))
        self.brokerUrl = kwargs.get('brokerUrl', r'localhost')
        self.brokerPort = kwargs.get('brokerPort', 1883)
        self.timeout = kwargs.get('timeout', 60)
        self.doEncrypt = kwargs.get('doEncrypt', False)
        self.doAuth = kwargs.get('doAuth', False)
        self.client = None
        self.logger = None
        self.subscriptions = None

        self.initConfig()

    def initConfig(self, **kwargs):
        self.setupLogger()
        self.logger.info('Initializing mqttClientDemo')
        self.client = mqtt.Client(clean_session=True)
        self.subscriptions = []
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def setupLogger(self):
        self.logger = logging.getLogger(self.clientName)                            # Logging prefaced with client name
        handlers = [logging.FileHandler(_LOG_FILE_NAME), logging.StreamHandler()]   # Log to file and command window
        logging.basicConfig(encoding='utf-8', level=logging.INFO, handlers=handlers)

    def checkClassSupport(self):
        assert self.doEncrypt == False, 'Encryption not currently supported. Please change connection parameters and retry'
        assert self.doAuth == False, 'Authentication not currently supported. Please change connection parameters and retry'

    def connect(self):
        self.checkClassSupport()
        self.logger.info('Attempting connection to {} broker on port {}'.format(self.brokerUrl, self.brokerPort))
        if url_ok:
            self.client.connect(self.brokerUrl, self.brokerPort, self.timeout)
        else:
            self.logger.info('Connection to {} on port {} failed. Unable to reach broker.'.format(self.brokerUrl, self.brokerPort))

        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected with result code {}".format(str(rc)))
        for topic in self.subscriptions:
            self.subscribe(topic)

    def on_message(self, client, userdata, msg):
        self.logger.info(' << ' + msg.topic + " " + str(msg.payload))

    def reconnect(self):
        self.client.reconnect()

    def disconnect(self):
        self.logger.info('Disconnecting')
        self.client.disconnect()

    def subscribe(self, topic):
        self.logger.info('Subscribing to {}'.format(topic))
        self.client.subscribe(topic)

    def unsubscribe(self, topic):
        self.client.unsubscribe(topic)
        self.subscriptions.remove(topic)

    def publish(self, topic, payload=None, qos=0, retain=False):
        self.logger.info(' >> ' + topic + '" ' + str(payload))
        self.client.publish(topic, payload, qos, retain)
