# Generated by Django 3.2.4 on 2022-07-13 20:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("drevo", "0017_categoryexpert"),
    ]

    operations = [
        migrations.CreateModel(
            name="InterviewExpertResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "is_yesno_answer_argument",
                    models.BooleanField(
                        verbose_name="Аргумент вопроса Да-Нет? (нет - контраргумент)"
                    ),
                ),
                (
                    "is_incorrect_answer",
                    models.BooleanField(verbose_name="некорректный ответ"),
                ),
                (
                    "согласен",
                    models.BooleanField(verbose_name="Эксперт согласен с ответом?"),
                ),
                (
                    "comment_type",
                    models.CharField(
                        choices=[
                            ("ARGUM", "Аргумент"),
                            ("KONTR", "Контраргумент"),
                            ("INVAL", "Некорректность"),
                        ],
                        max_length=5,
                        verbose_name="тип комментария",
                    ),
                ),
                ("comment", models.TextField(verbose_name="Текст дополнения")),
                ("updated", models.DateTimeField()),
                (
                    "new_answer_text",
                    models.TextField(verbose_name="новый ответ от эксперта"),
                ),
                (
                    "admin_comment",
                    models.TextField(verbose_name="Комментарий администратора"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("APPRVE", "Принят"),
                            ("REJECT", "Не принят"),
                            ("ANSDPL", "Дублирует ответ"),
                            ("RESDPL", "Дублирует предложение"),
                        ],
                        max_length=6,
                    ),
                ),
                (
                    "admin_reviewer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Администратор",
                    ),
                ),
                (
                    "answer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="as_answer_interviews",
                        to="drevo.znanie",
                        verbose_name="Ответ",
                    ),
                ),
                (
                    "expert",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="interview_results",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Ответивший эксперт",
                    ),
                ),
                (
                    "new_answer",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="made_in_interview",
                        to="drevo.znanie",
                        verbose_name="Новый ответ",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ответ на интервью",
                "verbose_name_plural": "Ответы на интервью",
                "ordering": ("-updated",),
            },
        ),
    ]
