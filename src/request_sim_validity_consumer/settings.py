from loguru_ext import set_serialize, setup_loguru_logging_intercept

from pydantic import BaseSettings


class Settings(BaseSettings):
    # faust variables
    WEB_HOST: str = '0.0.0.0'
    WEB_PORT: int = 8004
    SERVICE_NAME: str = 'request-sim-card-consumer'
    # adapter_smev variables
    ADAPTER_SMEV_WSDL: str = 'http://smev-test.corp.motiv:7576/ws/SMEVServiceAdapterService?WSDL'
    MNEMONIC: str = "U131101"
    # kafka variables
    KAFKA_BROKER_URL: str = "kafka01.corp.motiv:9093;kafka02.corp.motiv:9093;kafka03.corp.motiv:9093"
    KAFKA_TOPIC_NAME: str = 'GeneralDataRequest'
    KAFKA_TOPIC_NAME_RESP: str = 'GeneralDataResponse'
    KAFKA_TOPIC_PREFIX: str = 'smev.mvd.staging.'
    KAFKA_USERNAME: str = 'motiv_smev_staging'
    KAFKA_PASSWORD: str = ''
    # prometheus variables
    PROMETHEUS_PORT: int = 7004
    # logging variables
    LOGGING_LEVEL: str = "DEBUG"
    SERIALIZE: bool = False


settings = Settings(
    _env_file='.env',
    _env_file_encoding='utf-8'
)

setup_loguru_logging_intercept(level=settings.LOGGING_LEVEL,
                               enable_modules=tuple(settings.ENABLE_MODULES.split('|')),
                               disable_modules=tuple(settings.DISABLE_MODULES.split('|')))

if settings.SERIALIZE:
    set_serialize(settings.LOGGING_LEVEL)

logger = logging.getLogger(__name__)
logger.info('Настройки приложения инициализированы.')
