from alpaca.data.live import StockDataStream
from kafka import KafkaProducer
import json, os, logging

#Define Logging
log = logging.getLogger(__name__)

#Capture Brokers from environment variables
brokers = os.environ.get('BOOTSTRAP_SERVERS')

#Create Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=brokers, #Brokers List
    api_version=(3,5,1),
    # For mTLS auth:
    security_protocol='SASL_SSL',
    ssl_check_hostname=True,
    sasl_mechanism=os.environ.get("KAFKA_SASL_MECHANISM"),
    sasl_plain_username=os.environ.get("KAFKA_SASL_USERNAME"),
    sasl_plain_password=os.environ.get("KAFKA_SASL_PASSWORD"),
    
    value_serializer=lambda v: json.dumps(v).encode('utf-8'), #Serialization Method
    acks=(1) #Number of ACKs to wait on. (0= None, 1=Partition Leader, All= All Brokers with the partion)
)

#Post messages into Kafka Topics
async def post_bars(b):
    print('trade_bars', b)
    producer.send('trade_bars', value=str(b))
    producer.flush()

async def post_trade(t):
    print('trade', t)
    producer.send('trade', value=str(t))
    producer.flush()

async def post_quote(q):
    print('quote', q)
    producer.send('quote', value=str(q))
    producer.flush()

async def post_crypto_trade(t):
    print('crypto_trade', t)
    producer.send('crypto_trade', value=str(t))
    producer.flush()

#Main Function that create Alpaca Stream Subscriptions
def main():
    logging.basicConfig(level=logging.INFO)

    # keys are required for live data
    #crypto_stream = CryptoDataStream("api-key", "secret-key")
    stock_stream = StockDataStream(os.environ.get("API_KEY"), os.environ.get("SECRET_KEY"))
    #option_stream = OptionDataStream("api-key", "secret-key")

    stock_stream.subscribe_quotes(post_quote, "QQQ")
    stock_stream.subscribe_quotes(post_quote, "AMZN")

    stock_stream.run()

if __name__ == "__main__":
    main()  
