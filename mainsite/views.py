# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.loader import get_template
from django.shortcuts import render,redirect

from django.http import HttpResponse
from datetime import datetime
from .models import Post

# Create your views here.

def homepage_prev(request):
	posts=Post.objects.all()
	post_lists=list()
	for count,post in enumerate(posts):
		post_lists.append("No.{}:".format(str(count+1))+str(post)+"<br>")
		post_lists.append("<small>" +str(post.body.encode('utf-8'))+"</samll><br><br>")
	return HttpResponse(post_lists)


def homepage(request):
	template=get_template('index.html')
	posts=Post.objects.all()
	now=datetime.now()
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
	html='''
	<!DOCTYPE html>
	<html>
	<head><title>About Myself</title></head>
	<body>
	<h2>Li-Bin</h2>
	<hr>
	<p>
	Hi, I am Li-Bin. Welcome to my blog !
	</p>		
	</body>
	</html>
	'''
	return HttpResponse(html)

def listing(request):
	html='''
	<!DOCTYPE html>
	<html>
	<head>
	<meta charset='utf-8'>
	<title>博客文章列表</title>
	</head>	
	<body>
	<h2>以下是我的博客列表</h2>
	<hr>
	<table width=400 border=1 bgcolor='#ccffcc'>
	{}
	</table>
	</body>
	</html>
	'''
	posts=Post.objects.all()
	tags='<tr><td>序号</td><td>标题</td><td>时间</td></tr>'
	for p in posts:
		tags=tags + '<tr><td>{}</td>'.format(p.slug)
		tags=tags + '<td>{}</td>'.format(p.title)
		tags=tags + '<td>{}</td></tr>'.format(p.pub_date)

	return HttpResponse(html.format(tags))





