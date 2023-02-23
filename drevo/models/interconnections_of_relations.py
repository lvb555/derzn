from django.db import models
from .knowledge_kind import Tz
from .relation_type import Tr


class AllowedRelationCombinations(models.Model):
    """
    Таблица хранящая список разрешенных комбинаций вида 'Вид знания - Вид связи - Вид знания'
    """
    base_knowledge_type = models.ForeignKey(
        Tz, related_name='init_knowledge_types', on_delete=models.CASCADE, null=True, blank=True        
    )
    relation_type = models.ForeignKey(
        Tr, related_name='relation_types', on_delete=models.CASCADE, null=True, blank=True
    )
    related_knowledge_type = models.ForeignKey(
        Tz, related_name='relate_knowledge_types', on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        verbose_name = ("Взаимосвязь видов")
        verbose_name_plural = ("Взаимосвязи видов")
        ordering = ['pk']

    def __str__(self):
        try:
            return f"""
            Взаимосвязь отношений БЗ:{self.base_knowledge_type.name}, 
            ВС: {self.relation_type.name}, 
            СЗ: {self.related_knowledge_type.name}
            """
        except AttributeError:
            return f"""
            Взаимосвязь отношений БЗ:{self.initial_knowledge_type.name}, 
            ВС: {self.relation_type.name}
            """