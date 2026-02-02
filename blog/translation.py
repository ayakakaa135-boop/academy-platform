"""
Translation configuration for blog app
ضع هذا الملف في: blog/translation.py
"""
from modeltranslation.translator import translator, TranslationOptions
from .models import BlogCategory, Post


class BlogCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'excerpt', 'content')


translator.register(BlogCategory, BlogCategoryTranslationOptions)
translator.register(Post, PostTranslationOptions)