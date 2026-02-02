"""
Translation configuration for courses app
ضع هذا الملف في: courses/translation.py
"""
from modeltranslation.translator import translator, TranslationOptions
from .models import Category, Course, Lesson


class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


class CourseTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


class LessonTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


translator.register(Category, CategoryTranslationOptions)
translator.register(Course, CourseTranslationOptions)
translator.register(Lesson, LessonTranslationOptions)