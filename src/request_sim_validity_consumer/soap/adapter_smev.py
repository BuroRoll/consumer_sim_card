from zeep import AnyObject

from request_sim_validity_consumer.soap.schema_loader import Loader
from request_sim_validity_consumer.settings import settings
from request_sim_validity_consumer.msg_models import Request
from request_sim_validity_consumer.soap import SoapClient


class AdapterSmev(SoapClient):
    def __init__(self, uri=settings.ADAPTER_SMEV_WSDL):
        super(AdapterSmev, self).__init__(uri)
        self.mnemonic = settings.MNEMONIC
        self.factory = self.client.type_factory('urn://x-artefacts-smev-gov-ru/services/service-adapter/types')
        self.loader = Loader()

    async def build(self, content, client_id):
        factory = self.factory
        primary_content = AnyObject(content._xsd_elm, content)

        request_content = factory.RequestContentType(
            content=factory.Content(
                MessagePrimaryContent=primary_content
            )
        )

        linked_group = factory.LinkedGroupIdentity(
            refClientId=f'{client_id}',
            refGroupId=f'{client_id}'
        )
        routing_info = factory.RoutingInformationType(
            DynamicRouting=factory.DynamicRoutingType(
                DynamicValue=f'DEV'
            ),
            RegistryRouting=factory.RegistryRoutingType(
                RegistryRecordRouting=factory.RegistryRecordRoutingType(
                    RecordId=1,
                    UseGeneralRouting=False,
                    DynamicRouting=factory.DynamicRoutingType(
                        DynamicValue=f'DEV'
                    )
                )
            )
        )

        meta = factory.RequestMetadataType(
            clientId=f'{client_id}',
            linkedGroupIdentity=linked_group,
            RoutingInformation=routing_info
        )
        msg = factory.RequestMessageType(
            RequestMetadata=meta,
            RequestContent=request_content
        )
        return msg

    async def _send_request_and_get_response(self, operation_name, **kwargs):
        response = await self.send_soap_request(operation_name, itSystem=self.mnemonic, **kwargs)
        return response

    async def request_sim_card_validity(self, request: Request, client_id: str):
        get_send_message_element = self.loader.get_element('geps-smev3-2.0.2',
                                                           'GetSendMessageRequest')
        record_content = get_send_message_element(
            **{
                "User": {
                    "PersonDocument": {
                        "DocSeries": request.series,
                        "DocNumber": request.number,
                        "DocType": 'RF_PASSPORT',
                    }
                },
                "Param": [
                    {
                        'Name': 'orgName',
                        'Value': request.orgname
                    },
                    {
                        'Name': 'operatorName',
                        'Value': 'Мотив'
                    },
                    {
                        'Name': 'routeNumber',
                        'Value': self.mnemonic
                    },
                    {
                        'Name': 'corpPhoneData',
                        'Value': request.corp_phone
                    }
                ]
            }
        )
        record_content = AnyObject(record_content._xsd_elm, record_content)
        request = self.loader.get_element('geps-smev3-2.0.2',
                                          'Request')
        element = request(
            **{
                'GeneralData': {
                    'Settings': {
                        'ReadingNotification': False
                    },
                    'MessageType': 'SIM_CARD'
                },
                'Registry': {
                    'RegistryRecord': {
                        'RecordId': 1,
                        'Record': {
                            'RecordContent': record_content
                        }
                    }
                }
            }
        )
        msg = await self.build(content=element, client_id=client_id)
        response = await self._send_request_and_get_response('Send', RequestMessage=msg)

        return response
