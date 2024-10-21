from django.contrib import admin
from .models import Course, Article, Content, VideoPlayer, Quiz, UserPerformance,Hyperlink

# Customizing admin for the Course model
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'slug')
    search_fields = ('course_name',)
    prepopulated_fields = {'slug': ('course_name',)}
# # Customizing admin for the Hyperlink model
class HyperlinkAdmin(admin.ModelAdmin):
    list_display = ('hyper_link_word', 'slug','hyper_link_word_url')
    search_fields = ('hyper_link_word',)
    prepopulated_fields = {'slug': ('hyper_link_word',)}

# Customizing admin for the Article model
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('article_name', 'course_name', 'slug', 'article_video_url', 'display_hyperlinks')
    search_fields = ('article_name', 'course_name__course_name')
    list_filter = ('course_name',)
    prepopulated_fields = {'slug': ('article_name',)}

    # Method to display hyperlinks
    def display_hyperlinks(self, obj):
        return ", ".join([hyperlink.hyper_link_word for hyperlink in obj.hyperlinks.all()])
    display_hyperlinks.short_description = 'Hyperlinks'



# Customizing admin for the VideoPlayer model
class VideoPlayerAdmin(admin.ModelAdmin):
    list_display = ('video_title', 'channel_name', 'article')
    search_fields = ('video_title', 'channel_name')
    list_filter = ('channel_name',)

# Customizing admin for the Quiz model
class QuizAdmin(admin.ModelAdmin):
    list_display = ('article', 'question')
    search_fields = ('article', 'question')  # Search by article name and question
    list_filter = ('article',)

# Customizing admin for the UserPerformance model
class UserPerformanceAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)
    filter_horizontal = ('watched_videos',)  # Allows many-to-many field to be displayed as a filter

# Registering models with custom admin classes
admin.site.register(Course, CourseAdmin)
admin.site.register(Hyperlink, HyperlinkAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Content)
admin.site.register(VideoPlayer, VideoPlayerAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(UserPerformance, UserPerformanceAdmin)
