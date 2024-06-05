from kafka import KafkaConsumer
import os
import alpaca_pb2 as ProtoAlpaca

#Import Bootstrap server from environment variable
brokers = os.environ.get('VPCE_SCRAMBROKERS')

#Create Consumer
consumer = KafkaConsumer(
    'quote','trade','trade_bars', #topics to consume
    group_id='consumer_python', #local consumer name
    bootstrap_servers=brokers, #Brokers List
    api_version=(3,5,1),
    # For mTLS auth:
    security_protocol='SASL_SSL',
    ssl_check_hostname=True,
    sasl_mechanism=os.environ.get("KAFKA_SASL_MECHANISM"),
    sasl_plain_username=os.environ.get("KAFKA_SASL_USERNAME"),
    sasl_plain_password=os.environ.get("KAFKA_SASL_PASSWORD"),
)

print("Starting Kafka Consumer with brokers at ", brokers)

quote = ProtoAlpaca.quote()
trade = ProtoAlpaca.trade()
bars = ProtoAlpaca.bars()

# Loop to consume messages and Print details.
for message in consumer:
    if message.topic == 'quote':
        quote.ParseFromString(message.value)
        print (quote)    
        quote.Clear()
    elif message.topic == 'trade':
        trade.ParseFromString(message.value)
        print (trade)    
        trade.Clear()
    elif message.topic == 'trade_bars':
        bars.ParseFromString(message.value)
        print (bars)    
        bars.Clear()