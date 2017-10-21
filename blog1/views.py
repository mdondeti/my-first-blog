from django.shortcuts import render
from django.utils import timezone
from .models import Post
from django.shortcuts import render, get_object_or_404
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import LanguageTranslatorV2 as LanguageTranslator

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    tone_analyzer = ToneAnalyzerV3(
        username='f86d18cc-a579-4b13-8ea6-1a80dd039208',
        password='rROy4mUncQDa',
        version='2016-05-19 ')

    language_translator = LanguageTranslator(
        username='e68faa60-6e71-42e0-a5bc-a98e170c2826',
        password='DG6R6N3PNAnK')


    for post in posts:
        data = json.dumps(tone_analyzer.tone(text=post.text), indent=1)
        j = json.loads(data);
        post.info = j['document_tone']['tone_categories'][0]['tones']
        post.angerScore = post.info[0]['score']
        post.disgustScore = post.info[1]['score']
        post.fearScore = post.info[2]['score']
        post.joyScore = post.info[3]['score']
        post.sadScore = post.info[4]['score']
    translation = language_translator.translate(
        text=post.text,
        source='en',
        target='es')
    post.translatedText = json.dumps(translation, indent=2, ensure_ascii=False)
    return render(request, 'blog1/post_list.html', {'posts': posts})
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog1/post_detail.html', {'post': post})
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog1/post_edit.html', {'form': form})
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog1/post_edit.html', {'form': form})



