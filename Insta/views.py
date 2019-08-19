from django.views.generic import TemplateView, ListView, DetailView

from Insta.models import Post, InstaUser, Like, UserConnection
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.urls import reverse_lazy
from annoying.decorators import ajax_request
from Insta.forms import CustomUserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

class HelloDjango(TemplateView):
    template_name = 'home.html'

class PostView(LoginRequiredMixin, ListView):
	model = Post
	template_name = 'index.html'
	login_url = 'login'
class ExploreView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'explore.html'
    login_url = 'login'

    def get_queryset(self):
        return Post.objects.all().order_by('-posted_on')[:20]
class PostDetail(DetailView):
    model = Post
    template_name = "post_detail.html"

class PostCreateView(CreateView):
	    model = Post
	    template_name = "make_post.html"
	    fields = '__all__'

class PostUpdateView(UpdateView):
	    model = Post
	    template_name = "update_post.html"
	    fields = ('title',) #it can only update title

class PostDeleteView(DeleteView):
	    model = Post
	    template_name = "delete_post.html"
	    success_url = reverse_lazy('home')

class SignupView(CreateView):
	form_class = CustomUserCreationForm
	template_name = 'registration/signup.html'
	success_url = reverse_lazy('login')

class UserDetail(DetailView):
	    model = InstaUser
	    template_name = "user_profile.html"
	
class EditProfile(UpdateView):
	model = InstaUser
	template_name = "edit_profile.html"
	fields = ('username', 'profile_pic',) 

@ajax_request
def addLike(request):
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    try:
        like = Like(post=post, user=request.user)
        like.save()
        result = 1
    except Exception as e:
        like = Like.objects.get(post=post, user=request.user)
        like.delete()
        result = 0

    return {
        'result': result,
        'post_pk': post_pk
    }

@ajax_request
def toggleFollow(request):
    current_user = InstaUser.objects.get(pk=request.user.pk)
    follow_user_pk = request.POST.get('follow_user_pk')
    follow_user = InstaUser.objects.get(pk=follow_user_pk)

    try:
        if current_user != follow_user:
            if request.POST.get('type') == 'follow':
                connection = UserConnection(creator=current_user, following=follow_user)
                connection.save()
            elif request.POST.get('type') == 'unfollow':
                UserConnection.objects.filter(creator=current_user, following=follow_user).delete()
            result = 1
        else:
            result = 0
    except Exception as e:
        print(e)
        result = 0

    return {
        'result': result,
        'type': request.POST.get('type'),
        'follow_user_pk': follow_user_pk
    }


@ajax_request
def addComment(request):
    comment_text = request.POST.get('comment_text')
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    commenter_info = {}

    try:
        comment = Comment(comment=comment_text, user=request.user, post=post)
        comment.save()

        username = request.user.username

        commenter_info = {
            'username': username,
            'comment_text': comment_text
        }

        result = 1
    except Exception as e:
        print(e)
        result = 0

    return {
        'result': result,
        'post_pk': post_pk,
        'commenter_info': commenter_info
    }


