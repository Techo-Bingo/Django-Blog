# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.loader import get_template
from django.shortcuts import render,redirect

from django.http import HttpResponse,Http404
from datetime import datetime
from .models import Post
import random

# Create your views here.

def homepage_prev(request):
	posts=Post.objects.all()
	post_lists=list()
	for count,post in enumerate(posts):
		post_lists.append("No.{}:".format(str(count+1))+str(post)+"<br>")
		post_lists.append("<small>" +str(post.body.encode('utf-8'))+"</samll><br><br>")
	return HttpResponse(post_lists)

def bin_go(request):
	template=get_template('index.html')
	posts=Post.objects.all()
	now=datetime.now()
	html=template.render(locals())
	return HttpResponse(html)

def homepage(request):
	template=get_template('index_prev.html')
	posts=Post.objects.all()
	now=datetime.now()
	quotes=['今日事，今日做',
	'要收获，先付出',
	'知识就是力量',
	'个性就是命运']
	quote=random.choice(quotes)
	html=template.render(locals())
	return HttpResponse(html)

def showpost(request,slug):
	template=get_template('post.html')
	try:
		post=Post.objects.get(slug=slug)
		if post != None:
			html=template.render(locals())
			return HttpResponse(html)
	except:
		return redirect('/')
	
def about(request):
	template = get_template('about.html')
	quotes=['今日事，今日做',
	'要收获，先付出',
	'知识就是力量',
	'个性就是命运']
	html=template.render({'quote':random.choice(quotes)})
	#html=template.render()
	return HttpResponse(html)

def listing(request):
	posts=Post.objects.all()
	template = get_template('list.html')
	html = template.render({'posts':posts})
	return HttpResponse(html)

def disp_detail(request,sku):
	try:
		p=Post.objects.get(slug=sku)
	except Post.DoesNotExist:
		raise Http404('找不到指定的博客')

	template = get_template('disp.html')
	html = template.render({'blog':p})
	#return HttpResponse(html.format(p.title,p.title,tags))
	return HttpResponse(html)

