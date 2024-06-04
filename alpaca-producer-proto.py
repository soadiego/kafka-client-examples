from alpaca.data.live import StockDataStream
from kafka import KafkaProducer
import json, os, logging
import alpaca_pb2 as ProtoAlpaca

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
    trade_bars = ProtoAlpaca.bars()
    trade_bars.type = "trade_bars"
    trade_bars.symbol = b.symbol
    trade_bars.time = str(b.timestamp)
    trade_bars.open = b.open
    trade_bars.high = b.high
    trade_bars.low = b.low
    trade_bars.close = b.close
    trade_bars.volume = b.volume

    print('trade_bars', trade_bars.SerializeToString())
    producer.send('trade_bars', value=trade_bars)
    producer.flush()

async def post_trade(t):
    trade = ProtoAlpaca.trade()
    trade.type = "trade"
    trade.symbol = t.symbol
    trade.id = t.id
    trade.exchange = t.exchange
    trade.price = t.price
    trade.size = t.size
    trade.condition = str(t.conditions)
    trade.time = str(t.timestamp)
    trade.tape = t.tape

    print('trade_proto', trade.SerializeToString())
    producer.send('trade', value=str(t))
    producer.flush()

async def post_quote(q):
    quote = ProtoAlpaca.quote()
    quote.type = "quote"
    quote.symbol = q.symbol
    quote.ask_exchange = q.ask_exchange
    quote.ask_price = q.ask_price
    quote.ask_size = q.ask_size
    quote.bid_exchange = q.bid_exchange
    quote.bid_price = q.bid_price
    quote.bid_size = q.bid_size
    quote.condition = str(q.conditions)
    quote.time = str(q.timestamp)
    quote.tape = q.tape

    print('quote_proto', quote.SerializeToString())
    producer.send('quote', value=quote)
    producer.flush()

#Main Function that create Alpaca Stream Subscriptions
def main():
    logging.basicConfig(level=logging.INFO)

    # keys are required for live data
    #crypto_stream = CryptoDataStream("api-key", "secret-key")
    #option_stream = OptionDataStream("api-key", "secret-key")

    stock_stream = StockDataStream(os.environ.get("API_KEY"), os.environ.get("SECRET_KEY"))
    stock_stream.subscribe_quotes(post_quote, "QQQ")
    stock_stream.subscribe_quotes(post_quote, "AMZN")

    stock_stream.run()

if __name__ == "__main__":
    main()  
