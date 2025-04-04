from django.test import TestCase
from drevo.models import Znanie, Category, SpecialPermissions, Tz
from users.models import User
from drevo.utils.common import get_user_roles, UserRoles


class TestGetUserRoles(TestCase):
    def setUp(self):
        # Создаем тестовых пользователей
        self.regular_user = User.objects.create(
            username="regular_user",
            is_expert=False,
            is_director=False,
            is_redactor=False
        )
        
        self.expert_user = User.objects.create(
            username="expert_user",
            is_expert=True,
            is_director=False,
            is_redactor=False
        )
        
        self.director_user = User.objects.create(
            username="director_user",
            is_expert=False,
            is_director=True,
            is_redactor=False
        )
        
        self.redactor_user = User.objects.create(
            username="redactor_user",
            is_expert=False,
            is_director=False,
            is_redactor=True
        )

        # Создаем категории
        self.parent_category = Category.objects.create(name="Parent")
        self.child_category = Category.objects.create(
            name="Child",
            parent=self.parent_category
        )

        # Создаем знание
        self.tz = Tz.objects.create(name="Test Tz")
        self.knowledge = Znanie.objects.create(
            name="Test Knowledge",
            category=self.child_category,
            user=self.regular_user,
            tz=self.tz
        )

        # Создаем специальные разрешения
        self.expert_permissions = SpecialPermissions.objects.create(
            expert=self.expert_user
        )
        self.expert_permissions.categories.add(self.parent_category)

        self.director_permissions = SpecialPermissions.objects.create(
            expert=self.director_user
        )
        self.director_permissions.admin_competencies.add(self.parent_category)

    def test_regular_user_as_author(self):
        """Тест для обычного пользователя, который является автором"""
        roles = get_user_roles(self.regular_user, self.knowledge)
        assert len(roles) == 1
        assert UserRoles.author in roles

    def test_expert_user_with_permissions(self):
        """Тест для эксперта с соответствующими разрешениями"""
        roles = get_user_roles(self.expert_user, self.knowledge)
        assert len(roles) == 1
        assert UserRoles.expert in roles

    def test_director_user_with_permissions(self):
        """Тест для руководителя с соответствующими разрешениями"""
        roles = get_user_roles(self.director_user, self.knowledge)
        assert len(roles) == 1
        assert UserRoles.director in roles

    def test_redactor_user_with_expert_permissions(self):
        """Тест для редактора с правами эксперта"""
        # Добавляем редактору права эксперта
        redactor_permissions = SpecialPermissions.objects.create(
            expert=self.redactor_user
        )
        redactor_permissions.categories.add(self.parent_category)
        
        roles = get_user_roles(self.redactor_user, self.knowledge)
        assert len(roles) == 1
        assert UserRoles.editor in roles

    def test_user_without_category(self):
        """Тест для знания без категории"""
        knowledge_without_category = Znanie.objects.create(
            name="No Category Knowledge",
            user=self.regular_user,
            tz=self.tz
        )
        roles = get_user_roles(self.expert_user, knowledge_without_category)
        assert len(roles) == 0

    def test_user_without_permissions(self):
        """Тест для пользователя без специальных разрешений"""
        user_without_permissions = User.objects.create(
            username="no_permissions",
            is_expert=True
        )
        roles = get_user_roles(user_without_permissions, self.knowledge)
        assert len(roles) == 0

    def test_multiple_roles(self):
        """Тест на множественные роли"""
        # Создаем пользователя с несколькими ролями
        multi_role_user = User.objects.create(
            username="multi_role",
            is_expert=True,
            is_director=True
        )
        
        # Делаем его автором
        knowledge = Znanie.objects.create(
            name="Multi Role Knowledge",
            category=self.child_category,
            user=multi_role_user,
            tz=self.tz
        )
        
        # Добавляем разрешения
        permissions = SpecialPermissions.objects.create(expert=multi_role_user)
        permissions.categories.add(self.parent_category)
        permissions.admin_competencies.add(self.parent_category)
        
        roles = get_user_roles(multi_role_user, knowledge)
        assert len(roles) == 3
        assert UserRoles.author in roles
        assert UserRoles.expert in roles
        assert UserRoles.director in roles

    def test_different_role_combinations(self):
        """Тест для различных комбинаций ролей"""
        test_cases = [
            ({"is_expert": True}, [UserRoles.expert]),
            ({"is_director": True}, [UserRoles.director]),
            ({"is_redactor": True}, [UserRoles.editor]),
            ({"is_expert": True, "is_director": True}, [UserRoles.expert, UserRoles.director]),
        ]

        for user_data, expected_roles in test_cases:
            with self.subTest(user_data=user_data):
                user = User.objects.create(
                    username=f"user_{'_'.join(user_data.keys())}",
                    **user_data
                )

                # Создаем разрешения
                permissions = SpecialPermissions.objects.create(expert=user)
                permissions.categories.add(self.parent_category)
                permissions.admin_competencies.add(self.parent_category)

                roles = get_user_roles(user, self.knowledge)
                self.assertTrue(all(role in roles for role in expected_roles))