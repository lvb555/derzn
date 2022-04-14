from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import Http404, JsonResponse
from django.views.generic.edit import ProcessFormView
from ..models import Znanie, Comment
from ..models import Znanie, Comment
from loguru import logger


logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class CommentPageView(ProcessFormView):
    def get(self, request, pk, *args, **kwargs):
        if request.is_ajax():
            if pk:
                offset = Comment.COMMENTS_PER_PAGE
                is_last_page = False
                is_first_page = True

                last_comment_id = request.GET.get('last_comment_id')
                if last_comment_id:
                    if last_comment_id.isdigit():
                        last_comment_id = int(last_comment_id)
                    else:
                        raise Http404
                else:
                    last_comment_id = None

                znanie = get_object_or_404(Znanie, id=pk)

                if last_comment_id:
                    comments = znanie.comments.filter(
                        parent=None,
                        id__lt=int(last_comment_id),
                    ).select_related('parent', 'author')[0:offset]
                else:
                    comments = znanie.comments.filter(
                        parent=None,
                    ).select_related('parent', 'author')[0:offset]

                if not comments:
                    return JsonResponse(
                        {'data': render_to_string(
                            'drevo/comments_list.html'), 'is_last_page': True},
                        status=200
                    )

                if znanie.comments.filter(parent=None).last() in comments:
                    is_last_page = True
                if last_comment_id:
                    is_first_page = False

                context = {
                    'comments': comments,
                    'comment_max_length': Comment.CONTENT_MAX_LENGTH,
                    'is_authenticated': self.request.user.is_authenticated,
                    'offset': offset,
                    'is_first_page': is_first_page,
                    'is_last_page': is_last_page,
                }

                data = render_to_string('drevo/comments_list.html', context)
                return JsonResponse({'data': data, 'is_last_page': is_last_page}, status=200)

        raise Http404
