from rest_framework import serializers
from drevo.models import Category, Znanie


class CategorySerializer(serializers.ModelSerializer):
    children_count = serializers.SerializerMethodField()
    knowledge_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'children_count', 'knowledge_count']

    def get_children_count(self, obj):
        return obj.get_children().count()

    def get_knowledge_count(self, obj):
        return Znanie.objects.filter(category=obj).count()


class KnowledgeSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='tz.name', read_only=True)
    type_icon = serializers.SerializerMethodField()
    author = serializers.CharField(source='author.name', read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = Znanie
        fields = ['id', 'name', 'type_name', 'type_icon', 'author', 'url']

    def get_type_icon(self, obj):
        # Возвращаем путь к иконке в зависимости от типа
        type_icon_map = {
            'fact': '/static/drevo/img/knowledge_icons/fact.png',
            'table': '/static/drevo/img/knowledge_icons/table.png',
            # ... другие типы ...
        }
        return type_icon_map.get(obj.tz.name, '/static/drevo/img/knowledge_icons/fact.png')

    def get_url(self, obj):
        url = obj.get_absolute_url()
        return url
