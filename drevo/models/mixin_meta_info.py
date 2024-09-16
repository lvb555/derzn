import json
from typing import Any

from django.db import models


class MetaInfoMixin(models.Model):
    """ Миксин для добавления поля Метаинформация к моделям

        метаинформация - словарь с ключами и значениями,
        который хранятся в модели в формате JSON

        get_meta_info(key:str) - получить метаинформацию по ключу
        set_meta_info(key:str, data) - установить метаинформацию по ключу
    """
    meta_info = models.CharField(max_length=1024, blank=True, null=True, verbose_name="Метаинформация")

    class Meta:
        abstract = True

    def get_meta_info(self, key: str) -> Any | None:
        """ Получить метаинформацию у модели по ключу key
            Если метаинформации нет - вернет None
        """
        if self.meta_info:
            json_data = json.loads(self.meta_info)
            return json_data.get(key, None)
        else:
            return None

    def set_meta_info(self, key: str, data: Any):
        """ Устанавливает метаинформацию у модели по ключу key
            После надо вызвать save() у модели
        """
        if self.meta_info:
            json_data = json.loads(self.meta_info)
            json_data[key] = data
            self.meta_info = json.dumps(json_data, ensure_ascii=False)
        else:
            self.meta_info = json.dumps({key: data}, ensure_ascii=False)


