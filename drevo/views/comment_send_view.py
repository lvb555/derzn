from django.shortcuts import get_object_or_404 , redirect
from django.template.loader import render_to_string
from django.http import Http404, JsonResponse
from django.views.generic.edit import ProcessFormView
from ..models import Znanie, Comment
from users.models import User
from loguru import logger



logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class CommentSendView(ProcessFormView):
    def get(self, request, pk, *args, **kwargs):
        if request.is_ajax():
            user = self.request.user

            if not user.is_authenticated:
                return JsonResponse({}, status=403)

            if pk:
                parent_id = self.request.GET.get('parent')
                content = self.request.GET.get('content').strip()

                if not content:
                    raise Http404

                znanie = get_object_or_404(Znanie, id=pk)
                author = get_object_or_404(User, id=user.id)
                parent_comment = None
                if parent_id:
                    parent_comment = get_object_or_404(Comment, id=parent_id)

                new_comment = Comment.objects.create(
                    author=author,
                    parent=parent_comment,
                    znanie=znanie,
                    content=content,
                )
                context = {
                    'is_authenticated': user.is_authenticated,
                    'comment_max_length': Comment.CONTENT_MAX_LENGTH,
                }

                is_first_answer = True
                if parent_id and parent_comment.answers.count() > 1:
                    is_first_answer = False

                if parent_id and not is_first_answer:
                    context['comment'] = new_comment
                    data = render_to_string(
                        'drevo/comments_card.html', context)
                else:
                    context['comments'] = [new_comment]
                    data = render_to_string(
                        'drevo/comments_list.html', context)

                return JsonResponse(
                    {
                        'data': data,
                        'new_comment_id': new_comment.id,
                        'is_first_answer': is_first_answer
                    },
                    status=200
                )

        raise Http404


def like(request, pk):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, id=pk)
        if comment.likes.filter(id=request.user.id):
            comment.likes.remove(request.user)                      #повторный вызов убирает лайк
        else:
            comment.likes.add(request.user)
            comment.dislikes.remove(request.user)
        return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return redirect('users:login')

def dislike(request, pk):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, id=pk)
        if comment.dislikes.filter(id=request.user.id):
            comment.dislikes.remove(request.user)                       #повторный вызов убирает дизлайк
        else:
            comment.dislikes.add(request.user)
            comment.likes.remove(request.user)
        return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return redirect('users:login')
