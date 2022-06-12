from decimal import Decimal
from json import JSONEncoder
from uuid import UUID

import requests
from constance import config
from constance.backends.database.models import Constance
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from fcm_django.models import FCMDevice
from money.currency import Currency

from rc871_backend import settings


class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, QuerySet):
            try:
                data = dict(obj)
            except ValueError:
                data = list(obj)
            return data
        else:
            return JSONEncoder.default(self, obj)


def get_settings(allow_settings):
    setting_list = []
    for key, options in getattr(settings, 'CONSTANCE_CONFIG', {}).items():
        if key in allow_settings and key not in [
            "INTELLIGENT_ASSIGNMENT_CONTROL", "PREFIX_APP", "TOKEN_ERP", "API_NESTLE", "TOKEN_NESTLE", "ICON_FCM"
        ]:
            default, help_text = options[0], options[1]
            try:
                item = Constance.objects.get(key=key)
                value = item.value
                id = item.id
            except ObjectDoesNotExist:
                id = None
                value = getattr(config, key)
            data = {
                'id': id,
                'key': key,
                'default': default,
                'help_text': help_text,
                'value': value}
            setting_list.append(data)
    return setting_list


def send_fcm_external(title: str, body: str, registration_tokens=[]):
    try:
        image = Constance.objects.get(key="ICON_FCM").value
    except ObjectDoesNotExist:
        getattr(config, "ICON_FCM")
        image = Constance.objects.get(key="ICON_FCM").value

    try:
        params = {
            "notification": {
                "title": title,
                "body": body,
                "image": image
            },
            "token": registration_tokens
        }
        response = requests.post('http://127.0.0.1:5000/send', json=params)
        if response.status_code == 200:
            resp = response.json()
            if len(resp['deactivate_devices']) > 0:
                FCMDevice.objects.filter(registration_id__in=resp['deactivate_devices']).update(active=False)
                FCMDevice.objects._delete_inactive_devices_if_requested(resp['deactivate_devices'])
        return response
    except ValueError as e:
        return e


def format_coin(coin):
    if coin == Currency.USD.value:
        coin_format = "$"
    elif coin == Currency.VEF.value:
        coin_format = "Bs"
    else:
        coin_format = coin
    return coin_format
