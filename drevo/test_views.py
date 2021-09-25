"""
Test of views


Name of test classes:
Test{View name}
"""

from django.test import TestCase
from .models import Znanie, Category, Tz, AuthorType, Author
from django.contrib.auth.models import User
from django.urls import reverse


class TestDrevoView(TestCase):

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
        
        for i in range(10):
            name = 'TestZnanie' + str(i)
            Znanie.objects.create(name=name,
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

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/drevo/')
        self.assertEqual(resp.status_code, 200)    
    
    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('drevo'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('drevo'))
        self.assertTemplateUsed(resp, 'drevo/drevo.html')        