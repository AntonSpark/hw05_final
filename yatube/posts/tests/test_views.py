from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, Follow

User = get_user_model()


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='test_user',
            email='testmail@gmail.com',
            password='Qwerty123',
        )
        cls.group = Group.objects.create(
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.author}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
            'posts/post_create.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_shows_correct_context(self):
        """Шаблон главной страницы сформирован корректным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        expected_context = self.post
        current_context = response.context['page_obj'][0]
        self.assertEqual(current_context, expected_context)

    def test_profile_page_shows_correct_context(self):
        """Шаблон страницы пользователя сформирован корректным контекстом."""
        profile_url = reverse(
            'posts:profile', kwargs={'username': self.author}
        )
        response = self.authorized_client.get(profile_url)
        current_context = response.context['author']
        expected_context = PostViewsTest.author
        self.assertEqual(current_context, expected_context)

    def test_post_page_shows_correct_context(self):
        """Шаблон страницы публикации сформирован корректным контекстом."""
        post_url = reverse('posts:post_detail', kwargs={'post_id': 1})
        response = self.authorized_client.get(post_url)
        current_context = response.context['post']
        expected_context = PostViewsTest.post
        self.assertEqual(current_context, expected_context)

    def test_group_page_shows_correct_context(self):
        """Шаблон страницы группы сформирован корректным контекстом."""
        group_url = reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        response = self.authorized_client.get(group_url)
        current_context = response.context['group']
        expected_context = PostViewsTest.group
        self.assertEqual(current_context, expected_context)

    def test_new_post_appears_on_pages(self):
        """Новый пост отображается на страницах index, group, profile"""
        expected_context = self.post
        urls_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': self.author}),
        ]
        for url in urls_pages:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(len(response.context['page_obj']), 1)
                current_context = response.context['page_obj'][0]
                self.assertEqual(current_context, expected_context)

    def test_new_post_does_not_appear_in_other_group(self):
        """
        Новый post не отображается в группе, для которой не был предназначен.
        """
        Group.objects.create(slug='other-test-slug')
        other_url = reverse(
            'posts:group_list', kwargs={'slug': 'other-test-slug'}
        )
        response = self.authorized_client.get(other_url)
        self.assertNotIn(PostViewsTest.post, response.context['page_obj'])


class FollowersTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='test_1')
        cls.user_2 = User.objects.create_user(username='test_2')
        cls.user_3 = User.objects.create_user(username='test_3')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание группы'
        )

    def setUp(self):
        self.unauthorized_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_2)

    def test_authorized_user_can_follow_authors(self):
        """Авторизованный пользователь может
        подписываться на других пользователей.
        """
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_1.username})
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_2, author=self.user_1).exists()
        )

    def test_unauthorized_user_can_not_follow_authors(self):
        """Неавторизованный пользователь не может
        подписываться на других пользователей.
        """
        followers_count = Follow.objects.all().count()
        self.unauthorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_1.username})
        )
        followers_count_check = Follow.objects.all().count()
        self.assertEqual(followers_count, followers_count_check)

    def test_user_can_unfollow_authors(self):
        """Пользователь может отписаться от автора."""
        Follow.objects.create(user=self.user_2, author=self.user_1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_2, author=self.user_1).exists()
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_1.username})
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user_2, author=self.user_1).exists()
        )

    def test_post_on_follow_page_of_follower(self):
        """Новая запись пользователя появляется
        в ленте тех, кто на него подписан.
        """
        Follow.objects.create(user=self.user_2, author=self.user_1)
        post = Post.objects.create(
            text='Тестовый пост для проверки подписок',
            author=self.user_1,
            group=self.group,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        posts_list = response.context['page_obj']
        self.assertIn(post, posts_list)

    def test_no_post_on_follow_page_of_non_follower(self):
        """Новая запись пользователя не появляется
        в ленте тех, кто на него не подписан.
        """
        self.authorized_client.force_login(self.user_3)
        post = Post.objects.create(
            text='Тестовый пост для проверки подписок',
            author=self.user_1,
            group=self.group,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        posts_list = response.context['page_obj']
        self.assertNotIn(post, posts_list)