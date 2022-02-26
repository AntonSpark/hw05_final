from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, Follow

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.user = User.objects.create_user(username='no_name')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Tekst',
            group=cls.group
        )
        cls.url_index = '/'
        cls.url_group_slag = f'/group/{cls.group.slug}/'
        cls.url_profile_noUserName = f'/profile/{cls.user}/'

    def setUp(self):
        self.authorized_client = Client(self.user)
        self.authorized_client.force_login(self.user)

    def test_pages_show_correct(self):
        pages_list = [
            self.url_index,
            self.url_group_slag,
            self.url_profile_noUserName
        ]
        for url in pages_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Недоступна страница {url}')

    def test_redirect_if_not_logged_in(self):
        """Адрес "/create" перенаправляет
        неавторизованного пользователя"""
        response = ('/create/')
        self.assertTrue(response, '/accounts/login/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон,
        для неавторизованного пользователя"""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_home_url_uses_correct_template(self):
        """Страница '/create' использует шаблон 'posts/create_post.html'
         для авторизованного пользователя"""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/post_create.html')

    def test_edit_page_correct_template(self):
        '''Адрес '/edit' редактирования поста использует шаблон create.html
        для автора поста'''
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}))
        self.assertTemplateUsed(response, 'posts/post_create.html')

    def test_follow_index(self):
        """Страница избранных авторов доступна
        только авторизованным пользователям"""
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_follow(self):
        """Функция подписки доступна
        только авторизованным пользователям"""
        username = PostURLTests.user.username
        response = self.authorized_client.get(f'/profile/{username}/follow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_profile_unfollow(self):
        """Функция отписки доступна
        только авторизованным пользователям"""
        Follow.objects.create(
            author=PostURLTests.user,
            user=self.user
        )
        username = PostURLTests.user.username
        response = self.authorized_client.get(f'/profile/{username}/unfollow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
