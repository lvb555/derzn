from django.test import TestCase

from users.models import User
from .models import Znanie, Relation, Tz, AuthorType, Author, Tr


class TestMixinMetaInfo(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='test_user', password='test_password')
        test_author_type = AuthorType.objects.create(name="TestAuthorType")

        author = Author.objects.create(
            name="TestAuthor", info="Test info", atype=test_author_type
        )

        tz = Tz.objects.create(name="TestTz", is_systemic=False)
        Znanie.objects.create(name='test_1', tz=tz, user=user)
        Znanie.objects.create(name='test_2', tz=tz, user=user)

        tr = Tr.objects.create(name='TestTr')
        Relation.objects.create(bz=Znanie.objects.get(id=1),
                                rz=Znanie.objects.get(id=2),
                                author=author,
                                user=user,
                                tr=tr)

    def test_knowledge_meta(self):
        knowledge = Znanie.objects.get(id=1)
        self.assertEqual(knowledge.get_meta_info('key_1'), None)

        knowledge.set_meta_info('key_1', 'value_1')
        knowledge.save()

        knowledge2 = Znanie.objects.get(id=1)
        self.assertEqual(knowledge2.get_meta_info('key_1'), 'value_1')

    def test_relation_meta(self):
        relation = Relation.objects.get(id=1)
        self.assertEqual(relation.get_meta_info('key_1'), None)

        relation.set_meta_info('key_2', 'value_2')
        relation.save()

        relation2 = Relation.objects.get(id=1)
        self.assertEqual(relation2.get_meta_info('key_2'), 'value_2')

    def test_update_knowledge_meta(self):
        knowledge = Znanie.objects.get(id=1)

        knowledge.set_meta_info('key_1', 'value_1')
        knowledge.set_meta_info('key_2', 'value_2')
        knowledge.save()
        self.assertEqual(knowledge.get_meta_info('key_1'), 'value_1')
        self.assertEqual(knowledge.get_meta_info('key_2'), 'value_2')

        knowledge.set_meta_info('key_1', 'value_2')
        knowledge.set_meta_info('key_2', 'value_1')
        knowledge.save()
        self.assertEqual(knowledge.get_meta_info('key_1'), 'value_2')
        self.assertEqual(knowledge.get_meta_info('key_2'), 'value_1')

        knowledge.set_meta_info('key_1', None)
        knowledge.set_meta_info('key_2', None)
        knowledge.save()

        self.assertEqual(knowledge.get_meta_info('key_1'), None)
        self.assertEqual(knowledge.get_meta_info('key_2'), None)

    def test_update_relation_meta(self):
        relation = Relation.objects.get(id=1)

        relation.set_meta_info('key_1', 'value_1')
        relation.set_meta_info('key_2', 'value_2')
        relation.save()
        self.assertEqual(relation.get_meta_info('key_1'), 'value_1')
        self.assertEqual(relation.get_meta_info('key_2'), 'value_2')

        relation.set_meta_info('key_2', 'value_1')
        relation.set_meta_info('key_1', 'value_2')
        relation.save()
        self.assertEqual(relation.get_meta_info('key_2'), 'value_1')
        self.assertEqual(relation.get_meta_info('key_1'), 'value_2')

        relation.set_meta_info('key_1', None)
        relation.set_meta_info('key_2', None)
        relation.save()
        self.assertEqual(relation.get_meta_info('key_1'), None)
        self.assertEqual(relation.get_meta_info('key_2'), None)
