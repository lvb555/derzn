from django.db import Models


class Var(Models):
    knowledge = models.ForeignKey(to="drevo.Znanie", on_delete=models.CASCADE, verbose_name="Знание")
    name = models.CharField(max_length=50, verbose_name="Имя")

    class Meta:
        verbose_name = "Переменная"
        verbose_name_plural = "Переменные"
