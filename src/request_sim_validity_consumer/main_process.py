from request_sim_validity_consumer import AdapterSmev, get_metric
from request_sim_validity_consumer.msg_models import Request, Response

import logging

logger = logging.getLogger(__name__)


class MainProcess:
    def __init__(self, msg_key, request: Request, resp_topic):
        get_metric('REQUEST_CNT').inc()
        logger.info(f'Получен новый запрос на проверку данных владельца корпоративной сим-карты:\nClientId({msg_key})')
        self.adapter = AdapterSmev()
        self.client_id = msg_key.decode()
        self.request = request
        self.resp_topic = resp_topic

    async def start_processing(self):
        await self.send_request_sim_card_validity()

    async def send_request_sim_card_validity(self):
        try:
            response = await self.adapter.request_sim_card_validity(self.request, self.client_id)
        except Exception as e:
            get_metric('ERROR_SEND_CNT').inc()
            logger.exception('Ошибка при отправке запроса на проверку данных владельца корпоративной сим-карты')
            logger.error(e)
            await self.resp_topic.send(key=self.client_id, value=Response(code='NOT_SEND', description=f'{e}'))
            raise e
        else:
            logger.info(
                f'Запрос на проверку данных владельца корпоративной сим-карты успешно отправлен:\nClientId({response.MessageId})')
            await self.resp_topic.send(key=self.client_id, value=Response(code='SEND', description=None))
            get_metric('SUCCESSFUL_SEND_CNT').inc()
