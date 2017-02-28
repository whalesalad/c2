import json
import pprint
import socket

from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer

basename = str(__name__).split('.')[-1].replace('_', '-')
consumer_name = "%s-%s" % (basename, socket.gethostname(), )

KAFKA_HOSTS = [
    "stage-kafka-1.internal.egsense.net:9092",
    "stage-kafka-2.internal.egsense.net:9092",
    "stage-kafka-3.internal.egsense.net:9092"
]

def consume():
    message_count = 0

    kafka = KafkaClient(KAFKA_HOSTS)

    consumer = SimpleConsumer(client=kafka,
                              group='XXXXX-YYYYY-ZZZZZ',
                              topic='events',
                              iter_timeout=15,
                              max_buffer_size=1024*1024*2)

    consumer.seek(0, )

    for m in consumer:
        message_count += 1
        pprint.pprint(m.message.value)
        print message_count
        print

if __name__ == '__main__':
    consume()