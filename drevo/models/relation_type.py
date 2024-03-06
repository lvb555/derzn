from django.db import models


class Tr(models.Model):
    """
    Виды связей
    """

    _cache = None

    FOR = False
    AGAINST = True

    ARGUMENT_TYPES = (
        (FOR, "За"),
        (AGAINST, "Против"),
    )

    title = "Вид связи"
    name = models.CharField(max_length=255, verbose_name="Название", unique=True)
    order = models.PositiveSmallIntegerField(
        verbose_name="Порядок",
        help_text="укажите порядковый номер",
        default=0,
    )
    is_systemic = models.BooleanField(default=False, verbose_name="Системный?")
    is_argument = models.BooleanField(default=False, verbose_name="Доказательная связь")
    argument_type = models.BooleanField(
        choices=ARGUMENT_TYPES, default=FOR, verbose_name="Тип довода"
    )
    has_invert = models.BooleanField(
        editable=False, default=False, verbose_name="Доступна инверсия"
    )
    invert_tr = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="invert_rel_type",
        verbose_name="Инверсия",
        help_text="Только для инверсивных связей",
    )

    objects = models.Manager()

    def clean(self):
        if self.invert_tr is not None:
            self.has_invert = True
        else:
            self.has_invert = False

    @classmethod
    def t_(cls, item):
        """
        Возвращает экземпляр типа связи из кэша
        это справочник, инвалидация не предполагается
        для ускорения работы и упрощения кода
        пример использования: tr_type = Tr.t_('Состав')
        """
        # если нет данных - делаем заполнение кэша
        if cls._cache is None:
            cls._cache = {}
            for record in cls.objects.all():
                cls._cache[record.name.strip()] = record

        if item in cls._cache:
            return cls._cache[item]
        else:
            # попытаемся поискать - вдруг таблица изменилась
            result = cls.objects.get(name=item)
            if result:
                # добавляем в кэш
                cls._cache[item] = result
                return result
            else:
                raise ValueError(f"Не найден тип связи: {item}")

    class Meta:
        verbose_name = "Вид связи"
        verbose_name_plural = "Виды связи"
        ordering = (
            "order",
            "name",
        )

    def __str__(self):
        return self.name
