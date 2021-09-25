"""
Test of models


Name of test classes:
Test{Model name}

Name of test functions: 
test_{field name}_{attrubute name to be tested}
or
test_{method name}
"""

from django.test import TestCase
from .models import Znanie, Category, Tz

class TestCategory(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Set up non-modified objects used by all test methods
        Category.objects.create(name='TestCategory', 
                                content='Test content',
                                is_published=True
                                )

    # Testing 'name' field
    def test_name_verbose_name(self):
        category = Category.objects.get(id=1)
        verbose_name = category._meta.get_field('name').verbose_name
        self.assertEquals(verbose_name,'Название')

    def test_name_unique(self):
        category = Category.objects.get(id=1)
        unique = category._meta.get_field('name').unique
        self.assertEquals(unique, True)

    # Testing 'content' field
    def test_content_verbose_name(self):
        category = Category.objects.get(id=1)
        verbose_name = category._meta.get_field('content').verbose_name
        self.assertEquals(verbose_name,'Содержание')

    def test_content_max_length(self):
        category = Category.objects.get(id=1)
        max_length = category._meta.get_field('content').max_length
        self.assertEquals(max_length, 512)

    # Testing 'is_published' field
    def test_is_published_verbose_name(self):
        category = Category.objects.get(id=1)
        verbose_name = category._meta.get_field('is_published').verbose_name
        self.assertEquals(verbose_name,'Опубликовано?')

    def test_is_published_default(self):
        category = Category.objects.get(id=1)
        default = category._meta.get_field('is_published').default
        self.assertEquals(default, False)

    # Testing get_absolute_url 
    def test_(self):
        category = Category.objects.get(id=1)
        self.assertEquals(category.get_absolute_url(),'/drevo/category/1')

    
class TestTz(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Set up non-modified objects used by all test methods
        Tz.objects.create(name='TestTz', 
                          is_systemic=False
                         )

    # Testing 'name' field
    def test_name_verbose_name(self):
        tz = Tz.objects.get(id=1)
        verbose_name = tz._meta.get_field('name').verbose_name
        self.assertEquals(verbose_name,'Название')

    def test_name_unique(self):
        tz = Tz.objects.get(id=1)
        unique = tz._meta.get_field('name').unique
        self.assertEquals(unique, True)

    # Testing 'is_systemic' field
    def test_is_systemic_verbose_name(self):
        tz = Tz.objects.get(id=1)
        verbose_name = tz._meta.get_field('is_systemic').verbose_name
        self.assertEquals(verbose_name,'Системный?')

    def test_is_systemic_default(self):
        tz = Tz.objects.get(id=1)
        default = tz._meta.get_field('is_systemic').default
        self.assertEquals(default, False)