import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Post, Group, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='anton')
        cls.group = Group.objects.create(
            title='test',
            slug='supergroup_8u8907272363',
            description='Тестовый group для теста',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Просто текст',
            group=cls.group
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.form_data = {
            'text': 'Тестовый текст - создаем пост через форму',
            'group': cls.group.id,
            'image': cls.uploaded,
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в PostForm."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_object = Post.objects.order_by('-id').first()
        self.assertEqual(form_data['text'], last_object.text)
        self.assertEqual(form_data['group'], last_object.group.pk)


    def test_edit_post(self):
        form_data = {
            'text': 'Наконец я сдам 5 спринт',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_user = User.objects.create_user(username='auth')
        cls.unauthorized_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.authorized_user)
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.authorized_user,
        )
        cls.form_data = {
            'text': 'Тестовый текст - комментарий к посту',
            'author': cls.authorized_user
        }
        cls.reverse_link = reverse(
            'posts:add_comment',
            kwargs={'post_id': cls.post.id})

    def test_authorized_user_can_comment_post(self):
        """Авторизованный пользователь может прокомментировать пост."""
        self.authorized_client.post(
            self.reverse_link,
            data=self.form_data,
            follow=True
        )
        self.assertEqual(
            Comment.objects.get(text=self.form_data['text']).text,
            self.form_data['text']
        )

    def test_unauthorized_user_cannot_comment_post(self):
        """Неавторизованный пользователь не может прокомментировать пост."""
        comments_count = Comment.objects.count()
        response = self.unauthorized_client.post(
            self.reverse_link,
            data=self.form_data,
            follow=True
        )
        redirect = reverse('users:login')
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertRedirects(
            response,
            f"{redirect}?next={self.reverse_link}"
        )
