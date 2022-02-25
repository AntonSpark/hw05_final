from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': ('Текст поста'),
            'group': ('Группа')
        }
        help_texts = {
            'text': ('Текст нового поста.'),
            'group': ('Группа, к которой будет относиться пост')
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        lables = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Текст нового комментария',
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text) > 1:
            return text
        raise forms.ValidationError("Не заполнен текст комментария!")
