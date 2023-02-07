from prometheus_client import Counter

metrics = {
    'ERROR_SEND_CNT': Counter('error_send',
                              'Счетчик поступивших, но не обработанных из-за ошибки запросов на валидацию'),
    'REQUEST_CNT': Counter('request', 'Счетчик поступивших запросов на валидацию'),
    'SUCCESSFUL_SEND_CNT': Counter('successful_send', 'Счетчик успешно отправленных запросов на валидацию'),
    'ERROR_RESPONSE_CNT': Counter('error_response', 'Счётчик ошибок получений ответов')
}


def get_metric(name):
    if name in metrics.keys():
        pass
    else:
        metrics[name] = Counter(name.split('}')[-1], f"Counter of requests sent to the {name.split('}')[-1]} topic")

    return metrics[name]
