"""
Test of models


Name of test classes:
Test{Model name}

Name of test functions: 
test_{field name}_{attrubute name to be tested}
or
test_{class method name}
or
test_meta_{Meta class option}
"""

from django.test import TestCase
from .models import Znanie, Category, Tz, AuthorType, Author
from django.contrib.auth.models import User

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
    def test_get_absolute_url(self):
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


class TestAuthorType(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Set up non-modified objects used by all test methods
        AuthorType.objects.create(name='TestAuthorType')

    # Testing 'name' field
    def test_name_verbose_name(self):
        obj = AuthorType.objects.get(id=1)
        tested_property = obj._meta.get_field('name').verbose_name
        self.assertEquals(tested_property, 'Вид авторов')    

    # Testing Meta class options
    def test_meta_verbose_name(self):
        obj = AuthorType.objects.get(id=1)
        tested_property = obj._meta.verbose_name
        self.assertEquals(tested_property, 'Вид авторов')

    def test_meta_verbose_name_plural(self):
        obj = AuthorType.objects.get(id=1)
        tested_property = obj._meta.verbose_name_plural
        self.assertEquals(tested_property, 'Виды авторов')


class TestAuthor(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Set up non-modified objects used by all test methods
        AuthorType.objects.create(name='TestAuthorType')
        test_author_type = AuthorType.objects.get(id=1)
        Author.objects.create(name='TestAuthor',
                              info='Test info',
                              atype=test_author_type
                             )

    # Testing 'name' field
    def test_name_verbose_name(self):
        obj = Author.objects.get(id=1)
        tested_property = obj._meta.get_field('name').verbose_name
        self.assertEquals(tested_property, 'Имя')   

    # Testing 'info' field
    def test_info_verbose_name(self):
        obj = Author.objects.get(id=1)
        tested_property = obj._meta.get_field('info').verbose_name
        self.assertEquals(tested_property, 'Сведения об авторе') 

    def test_info_max_length(self):
        obj = Author.objects.get(id=1)
        tested_property = obj._meta.get_field('info').max_length
        self.assertEquals(tested_property, 2048)    

    # Testing 'photo' field
    def test_photo_verbose_name(self):
        obj = Author.objects.get(id=1)
        tested_property = obj._meta.get_field('photo').verbose_name
        self.assertEquals(tested_property, 'Фото')      

    def test_photo_upload_to(self):
        obj = Author.objects.get(id=1)
        tested_property = obj._meta.get_field('photo').upload_to
        self.assertEquals(tested_property, 'photos/authors/')   

    # Testing 'atype' field
    def test_atype_verbose_name(self):
        obj = Author.objects.get(id=1)
        tested_property = obj._meta.get_field('atype').verbose_name
        self.assertEquals(tested_property, 'Вид автора')          

    def test_atype_blank(self):
        obj = Author.objects.get(id=1)
        tested_property = obj._meta.get_field('atype').blank
        self.assertTrue(tested_property)

    # Testing Meta class options
    def test_meta_verbose_name(self):
        obj = Author.objects.get(id=1)
        tested_property = obj._meta.verbose_name
        self.assertEquals(tested_property, 'Автор')

    def test_meta_verbose_name_plural(self):
        obj = Author.objects.get(id=1)
        tested_property = obj._meta.verbose_name_plural
        self.assertEquals(tested_property, 'Авторы')        


class TestZnanie(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Set up non-modified objects used by all test methods
        User.objects.create(username='TestUser', password='testpassword')
        user = User.objects.get(id=1)
        AuthorType.objects.create(name='TestAuthorType')
        test_author_type = AuthorType.objects.get(id=1)
        Author.objects.create(name='TestAuthor',
                              info='Test info',
                              atype=test_author_type
                             )
        author = Author.objects.get(id=1)
        
        Category.objects.create(name='TestCategory', 
                                content='Test content',
                                is_published=True
                                )
        category = Category.objects.get(id=1)                                                         
        
        Tz.objects.create(name='TestTz', 
                          is_systemic=False
                         )
        tz = Tz.objects.get(id=1)
        
        Znanie.objects.create(name='TestZnanie',
                              category=category,
                              tz=tz,
                              content='Test content',
                              href='https://www.test.com',
                              source_com='Test source',
                              author=author,
                              user=user,
                              order=1,
                              is_published=False,
                              )

    # Testing 'name' field
    def test_name_verbose_name(self):
        obj = Znanie.objects.get(id=1)
        tested_property = obj._meta.get_field('name').verbose_name
        self.assertEquals(tested_property, 'Тема')

    def test_name_unique(self):
        obj = Znanie.objects.get(id=1)
        tested_property = obj._meta.get_field('name').unique
        self.assertTrue(tested_property)        

    # Testing 'category' field
    def test_category_verbose_name(self):
        obj = Znanie.objects.get(id=1)
        tested_property = obj._meta.get_field('category').verbose_name
        self.assertEquals(tested_property, 'Категория')

    def test_category_blank(self):
        obj = Znanie.objects.get(id=1)
        tested_property = obj._meta.get_field('category').blank
        self.assertTrue(tested_property)

    def test_category_related_model(self):
        obj = Znanie.objects.get(id=1)
        tested_property = str(obj._meta.get_field('category').related_model)
        self.assertEquals(tested_property, "<class 'drevo.models.Category'>")        

    # Testing 'tz' field
    def test_tz_verbose_name(self):
        obj = Znanie.objects.get(id=1)
        tested_property = obj._meta.get_field('tz').verbose_name
        self.assertEquals(tested_property, 'Вид знания')

    def test_tz_related_model(self):
        obj = Znanie.objects.get(id=1)
        tested_property = str(obj._meta.get_field('tz').related_model)
        self.assertEquals(tested_property, "<class 'drevo.models.Tz'>")

    # Testing 'content' field
    def test_content_verbose_name(self):
        obj = Znanie.objects.get(id=1)
        tested_property = obj._meta.get_field('content').verbose_name
        self.assertEquals(tested_property, 'Содержание')     

    # Testing get_absolute_url 
    def test_get_absolute_url(self):
        obj = Znanie.objects.get(id=1)
        self.assertEquals(obj.get_absolute_url(),'/drevo/znanie/1')

        

