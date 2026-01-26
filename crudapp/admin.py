from django.contrib import admin
from .models import Item, PersonalInfo, JobOffer, ChatbotTrainingData, ChatbotConversation
from .ml_chatbot import MLChatbotService

# Register your models here.
admin.site.register(Item)

@admin.register(PersonalInfo)
class PersonalInfoAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'title', 'email', 'phone', 'availability', 'updated_at']
    list_editable = ['availability']
    search_fields = ['full_name', 'email', 'title']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company_name', 'recruiter_name', 'recruiter_email', 'status', 'submitted_at']
    list_filter = ['status', 'work_type', 'submitted_at']
    search_fields = ['job_title', 'company_name', 'recruiter_name', 'recruiter_email']
    readonly_fields = ['submitted_at', 'reviewed_at']
    fieldsets = (
        ('Recruiter Information', {
            'fields': ('recruiter_name', 'recruiter_email', 'recruiter_company', 'recruiter_phone')
        }),
        ('Job Details', {
            'fields': ('job_title', 'company_name', 'job_description', 'location', 'work_type', 'salary_range', 'benefits', 'start_date')
        }),
        ('Additional Information', {
            'fields': ('additional_info', 'status', 'submitted_at', 'reviewed_at')
        }),
    )


@admin.register(ChatbotTrainingData)
class ChatbotTrainingDataAdmin(admin.ModelAdmin):
    list_display = ['intent', 'user_message_preview', 'response_preview', 'created_at']
    list_filter = ['intent', 'created_at']
    search_fields = ['user_message', 'response', 'intent']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Training Data', {
            'fields': ('user_message', 'intent', 'response')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_message_preview(self, obj):
        return obj.user_message[:50] + "..." if len(obj.user_message) > 50 else obj.user_message
    user_message_preview.short_description = 'User Message'
    
    def response_preview(self, obj):
        return obj.response[:50] + "..." if len(obj.response) > 50 else obj.response
    response_preview.short_description = 'Response'
    
    def save_model(self, request, obj, form, change):
        """Retrain the model after saving training data"""
        super().save_model(request, obj, form, change)
        # Retrain the model with updated data
        try:
            ml_chatbot = MLChatbotService()
            ml_chatbot.retrain_from_database()
        except Exception as e:
            print(f"Error retraining model: {e}")
    
    def delete_model(self, request, obj):
        """Retrain the model after deleting a single training data entry"""
        super().delete_model(request, obj)
        # Retrain the model with updated data
        try:
            ml_chatbot = MLChatbotService()
            ml_chatbot.retrain_from_database()
        except Exception as e:
            print(f"Error retraining model: {e}")
    
    def delete_queryset(self, request, queryset):
        """Retrain the model after deleting training data"""
        super().delete_queryset(request, queryset)
        # Retrain the model with updated data
        try:
            ml_chatbot = MLChatbotService()
            ml_chatbot.retrain_from_database()
        except Exception as e:
            print(f"Error retraining model: {e}")
    
    actions = ['retrain_model']
    
    def retrain_model(self, request, queryset):
        """Admin action to retrain the model"""
        try:
            ml_chatbot = MLChatbotService()
            success = ml_chatbot.retrain_from_database()
            if success:
                self.message_user(request, "Model retrained successfully!")
            else:
                self.message_user(request, "Failed to retrain model. Check if there's training data.", level='error')
        except Exception as e:
            self.message_user(request, f"Error retraining model: {str(e)}", level='error')
    retrain_model.short_description = "Retrain ML model with all training data"


@admin.register(ChatbotConversation)
class ChatbotConversationAdmin(admin.ModelAdmin):
    list_display = ['session_id_short', 'conversation_state', 'message_count', 'created_at', 'updated_at']
    list_filter = ['conversation_state', 'created_at']
    search_fields = ['session_id']
    readonly_fields = ['session_id', 'created_at', 'updated_at', 'conversation_history', 'context']
    
    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'conversation_state')
        }),
        ('Conversation Data', {
            'fields': ('conversation_history', 'context'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def session_id_short(self, obj):
        return obj.session_id[:20] + "..." if len(obj.session_id) > 20 else obj.session_id
    session_id_short.short_description = 'Session ID'
    
    def message_count(self, obj):
        if obj.conversation_history:
            return len(obj.conversation_history)
        return 0
    message_count.short_description = 'Messages'