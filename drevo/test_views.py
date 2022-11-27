"""
Test of views


Name of test classes:
Test{View name}
"""
import datetime

# from unittest import mock

# import pytest
import pytz as pytz
from django.test import TestCase

from .forms import DateNewForm
from .models import Znanie, Category, Tz, AuthorType, Author
from users.models import User
from django.urls import reverse
import time_machine


class TestDrevoView(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        User.objects.create(
            username="TestUser", password="testpassword", email="test@testuser.test"
        )
        user = User.objects.get(id=1)
        AuthorType.objects.create(name="TestAuthorType")
        test_author_type = AuthorType.objects.get(id=1)
        Author.objects.create(
            name="TestAuthor", info="Test info", atype=test_author_type
        )
        author = Author.objects.get(id=1)

        Category.objects.create(
            name="TestCategory", content="Test content", is_published=True
        )
        category = Category.objects.get(id=1)

        Tz.objects.create(name="TestTz", is_systemic=False)
        tz = Tz.objects.get(id=1)
        time_mocks = (
            datetime.datetime(2017, 4, 5, 0, 0, 0, tzinfo=pytz.utc),
            datetime.datetime(2022, 4, 30, 0, 0, 0, tzinfo=pytz.utc),
            datetime.datetime(2022, 5, 4, 0, 0, 0, tzinfo=pytz.utc),
            datetime.datetime(2022, 3, 30, 0, 0, 0, tzinfo=pytz.utc),
            datetime.datetime(2022, 3, 26, 0, 0, 0, tzinfo=pytz.utc),
            datetime.datetime(2022, 5, 7, 0, 0, 0, tzinfo=pytz.utc),
            datetime.datetime(2022, 5, 6, 0, 0, 0, tzinfo=pytz.utc),
            datetime.datetime(2022, 4, 30, 0, 0, 0, tzinfo=pytz.utc),
            datetime.datetime(2022, 4, 30, 0, 0, 0, tzinfo=pytz.utc),
            datetime.datetime(2022, 4, 30, 0, 0, 0, tzinfo=pytz.utc),
        )
        # tz = pytz.timezone('Europe/Moscow')
        for i in range(10):
            name = "TestZnanie" + str(i)
            with time_machine.travel(time_mocks[i]):
                Znanie.objects.create(
                    name=name,
                    category=category,
                    tz=tz,
                    content="Test content",
                    href="https://www.test.com",
                    source_com="Test source",
                    author=author,
                    user=user,
                    order=1,
                    is_published=False,
                )
        Znanie.objects.create(
            name="test_we_category2",
            tz=tz,
            # category=category,
            content="Empty category1",
            href="https://ya.ru",
            source_com="Best source",
            author=author,
            user=user,
            order=1,
            is_published=False,
        )
        # assert Znanie.objects.filter(name=f'{name}')[0].date == time_mocks[i]

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get("/drevo/")
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse("drevo"))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("drevo"))
        self.assertTemplateUsed(resp, "drevo/drevo.html")

    def test_view_of_new_knwoledge(self):
        resp = self.client.get(reverse("new_knowledge"))
        self.assertTemplateUsed(resp, "drevo/new_knowledge.html")
        self.assertEqual(resp.status_code, 200)

    def test_news_view_start(self):
        resp = self.client.get(reverse("new_knowledge"))
        form = resp.context["dform"]
        self.assertIsInstance(form, DateNewForm)
        knowledges_fltrd_q = resp.context["categorized_new_knowledges"]
        self.assertEqual(len(knowledges_fltrd_q), 1)
        # print(knowledges_fltrd_q)
        # print(knowledges_fltrd_q.keys())
        self.assertEqual(len(knowledges_fltrd_q[list(knowledges_fltrd_q.keys())[0]]), 3)

    def test_requested_news(self):
        resp = self.client.get(
            reverse("new_knowledge"), {"day": 8, "month": 5, "year": 2022}
        )
        self.assertIn(
            "знаний за истекший период не обнаружено".encode("utf8"), resp.content
        )

    def test_requested_wrong(self):
        resp = self.client.get(
            reverse("new_knowledge"), {"day": 3, "month": 2, "year": 2027}
        )
        self.assertNotIn(
            "Следующую дату можно будет ввести позже".encode("utf8"), resp.content
        )
        resp = self.client.get(
            reverse("new_knowledge"), {"day": 3, "month": 2, "year": -7}
        )
        self.assertIn("это значение больше либо равно".encode("utf8"), resp.content)
        resp = self.client.get(
            reverse("new_knowledge"),
            {
                "month": 2,
            },
        )
        self.assertIn("бязательн".encode("utf8"), resp.content, 2)

    def test_created_dates(self):
        date_4th_m = datetime.date(2022, 5, 4)
        zn1 = Znanie.objects.filter(date__gte=date_4th_m)
        zn2 = Znanie.objects.filter(date__gt=datetime.date.today())
        self.assertEqual(zn2.count(), 0)
        self.assertEqual(zn1.count(), 3)

    # @pytest.mark.skip
    def test_additional(self):
        addtnl_kn = Znanie.objects.filter(name="test_we_category2")[0]
        print(type(addtnl_kn.category))
        print(addtnl_kn.category)
        self.assertEqual(addtnl_kn.category, None)

    def test_additional_ctxt(self):
        resp = self.client.get(reverse("new_knowledge"))
        qry_set_new_kn = resp.context["categorized_new_knowledges"]
        self.assertIn("Дополнительные знания", qry_set_new_kn.keys())
