import zeep.transports
from zeep import AsyncClient
from zeep.plugins import HistoryPlugin
from zeep.exceptions import Fault
from lxml import etree
from zeep.cache import InMemoryCache
import logging

from request_sim_validity_consumer import metrics

logger = logging.getLogger(__name__)


class SoapClient:
    """Класс для обращения к SOAP сервису."""

    msg_sent = "Отправлен запрос"
    msg_success = "Получен успешный ответ"
    msg_received_with_error = "Получен ответ, содержащий ошибку"

    def __init__(self, uri):
        """Конструктор класса SoapClient.
        :param uri: URI на который выполняется запрос.
        """
        try:
            self._client = AsyncClient(wsdl=uri, plugins=[HistoryPlugin()],
                                       transport=zeep.transports.AsyncTransport(cache=InMemoryCache()))
            logger.info(f'Установлено подключение к {self.__class__.__name__}')
        except Exception as e:
            logger.exception(f'Не удалось создать {self.__class__.__name__}.\n Ошибка подключения к {uri}\n {e}')
            raise e

    @property
    def client(self):
        return self._client

    async def send_soap_request(self, operation_name, *args, **kwargs):
        """Отправка SOAP-запроса.

        :param operation_name: Название soap-метода.
        :raise: Fault: Ошибка сервера.

        :return: Объект ответа.
        :rtype: object.

        """
        try:
            response = await getattr(self.client.service, operation_name)(*args, **kwargs)
            logger.debug(f'{self.msg_sent} - {self.__class__.__name__}.{operation_name}:\n{self.last_sent_message}')
            logger.debug(f'{self.msg_success} - {self.__class__.__name__}.{operation_name}:'
                         f'\n{self.last_received_message}')
        except Fault as fault:
            response = fault.detail[0]
            self.report_fault_message(details=response, operation_name=operation_name)
            raise fault
        return response

    @property
    def last_sent_message(self):
        """Получение последнего сообщения отправленного в SOAP запрос.

        :return Последнее сообщение отправленное в SOAP.
        :rtype: str.

        """
        return etree.tostring(self.client.plugins[0].last_sent['envelope'], encoding='unicode', pretty_print=True)

    @property
    def last_received_message(self):
        """Получение последнего ответа из SOAP запроса.

        :return: Последней ответ из SOAP запроса.
        :rtype: str.

        """
        return etree.tostring(self.client.plugins[0].last_received['envelope'], encoding='unicode', pretty_print=True)

    def report_fault_message(self, details, operation_name):
        """Уведомление об ошибке.

        :param operation_name: Имя метода, при вызове которого произошла ошибка.
        :param details: Данные ошибки.

        """
        logger.warning(f'{self.msg_sent} - {self.__class__.__name__}.{operation_name}:\n{self.last_sent_message}')
        metrics.metrics['ERROR_RESPONSE_CNT'].inc()
        document = str(details)
        if hasattr(details, 'fault'):
            logger.error(f"Ошибка сервера: '{details.fault.faultstring}'\n\n{document}")
        else:
            logger.error(f'{self.msg_received_with_error} - {self.__class__.__name__}.{operation_name}:'
                         f'\n{self.last_received_message}\n{document}')
