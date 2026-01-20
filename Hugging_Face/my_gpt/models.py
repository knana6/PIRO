from django.db import models

class Conversation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    ROLE_CHOICES = (
        ("user", "user"),
        ("assistant", "assistant"), # 채팅이니까 2가지 역할 선언
    )

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField() #입력된 채팅 내용
    created_at = models.DateTimeField(auto_now_add=True) # 시간순서대로 나열 
