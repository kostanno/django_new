from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import BlogPost


from .forms import BlogPostForm


class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog/blogpost_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True).order_by('-created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Все статьи блога'
        return context


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blogpost_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['next_post'] = BlogPost.objects.filter(
            is_published=True,
            created_at__lt=post.created_at
        ).order_by('-created_at').first()
        context['previous_post'] = BlogPost.objects.filter(
            is_published=True,
            created_at__gt=post.created_at
        ).order_by('created_at').first()
        return context


class BlogPostCreateView(SuccessMessageMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blogpost_form.html'
    success_url = reverse_lazy('blog:post_list')
    success_message = "Статья успешно создана!"

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class BlogPostUpdateView(SuccessMessageMixin, UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blogpost_form.html'
    success_message = "Статья успешно обновлена!"

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class BlogPostDeleteView(SuccessMessageMixin, DeleteView):
    model = BlogPost
    template_name = 'blog/blogpost_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')
    success_message = "Статья успешно удалена!"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)