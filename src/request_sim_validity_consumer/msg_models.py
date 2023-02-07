import faust


class Request(faust.Record, serializer='json'):
    series: str
    number: str
    orgname: str
    corp_phone: str


class Response(faust.Record, serializer='json'):
    code: str
    description: str | None
