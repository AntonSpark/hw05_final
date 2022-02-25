from django.core.paginator import Paginator

from yatube.settings import POSTS_PER_PAGE


def pagination(request, selector, count=POSTS_PER_PAGE):
    paginator = Paginator(selector, count)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
