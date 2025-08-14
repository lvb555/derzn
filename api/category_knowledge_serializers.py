from rest_framework import serializers

from drevo.models import Category, Znanie


class CategorySerializer(serializers.ModelSerializer):
    children_count = serializers.IntegerField(read_only=True)
    knowledge_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "children_count", "knowledge_count"]

    def to_representation(self, instance):
        # Используем аннотации, которые были добавлены в queryset
        representation = super().to_representation(instance)
        representation["children_count"] = instance.children_count
        representation["knowledge_count"] = instance.knowledge_count
        return representation


class KnowledgeSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source="tz.name", read_only=True)
    type_icon = serializers.SerializerMethodField()
    author = serializers.CharField(source="author.name", read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = Znanie
        fields = ["id", "name", "type_name", "type_icon", "author", "url"]

    def get_type_icon(self, obj):
        # Возвращаем путь к иконке в зависимости от типа
        type_icon_map = {
            "Факт": "/static/drevo/img/knowledge_icons/fact.png",
            "Таблица": "/static/drevo/img/knowledge_icons/table.png",
            "Классификация": "/static/drevo/img/knowledge_icons/classification.png",
            "Группа": "/static/drevo/img/knowledge_icons/group.png",
            "Вопрос": "/static/drevo/img/knowledge_icons/question.png",
            "Тезис": "/static/drevo/img/knowledge_icons/thesis.png",
            "Цитата": "/static/drevo/img/knowledge_icons/quote.png",
            # ... другие типы ...
        }
        return type_icon_map.get(obj.tz.name, "/static/drevo/img/knowledge_icons/other.png")

    def get_url(self, obj):
        url = obj.get_absolute_url()
        return url
