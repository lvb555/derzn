from django.db.models import Q, Count, F, Prefetch
from rest_framework import serializers
from drevo.models import Znanie, Relation, Tr, Tz

class RelatedKnowledgeSerializer(serializers.ModelSerializer):
    knowledge_type = serializers.CharField(source='tz.name')
    knowledge_type_icon = serializers.SerializerMethodField()
    related_count = serializers.IntegerField(read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = Znanie
        fields = ['id', 'name', 'knowledge_type', 'knowledge_type_icon', 'url', 'related_count']

    def get_knowledge_type_icon(self, obj):
        return f"/icons/{obj.tz.id}.png"

    def get_url(self, obj):
        return obj.get_absolute_url()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['related_count'] = instance.related_count if hasattr(instance, 'related_count') else 0
        return representation


class RelationSerializer(serializers.ModelSerializer):
    relation_name = serializers.CharField(source='tr.name')
    knowledge = serializers.SerializerMethodField()

    class Meta:
        model = Relation
        fields = ['id', 'relation_name', 'knowledge']

    def get_knowledge(self, obj):
        # Используем предварительно загруженные данные
        related_znanie = obj.rz
        related_znanie.related_count = obj.rz_related_count if hasattr(obj, 'rz_related_count') else 0
        return RelatedKnowledgeSerializer(related_znanie).data


class KnowledgeRelationsSerializer(serializers.ModelSerializer):
    knowledge_type = serializers.CharField(source='tz.name')
    knowledge_type_icon = serializers.SerializerMethodField()
    related_count = serializers.IntegerField(read_only=True)
    url = serializers.SerializerMethodField()
    relations = serializers.SerializerMethodField()

    class Meta:
        model = Znanie
        fields = ['id', 'name', 'knowledge_type', 'knowledge_type_icon', 'url', 'related_count', 'relations']

    def get_knowledge_type_icon(self, obj):
        return f"/icons/{obj.tz.id}.png"

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_relations(self, obj):
        # Используем предварительно загруженные relations
        return RelationSerializer(obj.prefetched_relations, many=True).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['related_count'] = instance.relations_count
        return representation