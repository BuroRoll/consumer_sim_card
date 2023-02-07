import ssl
import faust
from prometheus_client import start_http_server
import logging

logger = logging.getLogger(__name__)

from request_sim_validity_consumer import settings
from request_sim_validity_consumer.main_process import MainProcess
from request_sim_validity_consumer.msg_models import Request, Response

ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH,
                                         cafile='motivca.crt')

app = faust.App(settings.SERVICE_NAME, broker=settings.KAFKA_BROKER_URL,
                web_host=settings.WEB_HOST, web_port=settings.WEB_PORT,
                broker_credentials=faust.SASLCredentials(
                    ssl_context=ssl_context,
                    mechanism="SCRAM-SHA-512",
                    username=settings.KAFKA_USERNAME,
                    password=settings.KAFKA_PASSWORD,
                )
                )
src_data_topic = app.topic(f'{settings.KAFKA_TOPIC_PREFIX}{settings.KAFKA_TOPIC_NAME}', value_type=Request)
resp_data_topic = app.topic(f'{settings.KAFKA_TOPIC_PREFIX}{settings.KAFKA_TOPIC_NAME_RESP}', value_type=Response)


@app.agent(src_data_topic)
async def on_event(stream) -> None:
    async for msg_key, msg_value in stream.items():
        await MainProcess(msg_key, msg_value, resp_data_topic).start_processing()


@app.task
async def on_started() -> None:
    logger.info('Starting prometheus server')
    start_http_server(port=settings.PROMETHEUS_PORT)


if __name__ == '__main__':
    app.main()
