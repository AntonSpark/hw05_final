from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post


User = get_user_model()


class CacheTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.no_user_name = 'noUserName'
        cls.user = User.objects.create_user(username=cls.no_user_name)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )


    def test_cache_index_page(self):
        content = self.client.get(reverse('posts:index')).content
        self.post.delete()
        content_cache = self.client.get(reverse('posts:index')).content
        self.assertEqual(content, content_cache, 'Не работает cache страницы')
        cache.clear()
        content_cache_clear = self.client.get(reverse('posts:index')).content
        self.assertNotEqual(content, content_cache_clear)
