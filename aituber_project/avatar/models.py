from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.username
    

class ShortTermMemory(models.Model):
    ROLE_CHOICES = [("user", "User"),("assistant", "Assistant"),]
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="messages")
    role = models.CharField(max_length=20,choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.role}"
    

class LongTermMemory(models.Model):
# 事実（例: 夜型） #好み(例: 海が好き） #感情傾向  #スキル・能力  #重要な出来事
    MEMORY_TYPES = [
        ("fact", "Fact"),
        ("preference", "Preference"),
        ("emotion", "Emotion"),
        ("skill", "Skill"),
        ("event", "Event"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="long_term_memories")

    memory_type = models.CharField(max_length=50, choices=MEMORY_TYPES)

    content = models.TextField()
    # 例: "ユーザーは低レイヤー技術に興味がある"

    importance = models.FloatField(default=0.5)
    # 0.0 ~ 1.0（どれくらい重要か）

    source_messages = models.ManyToManyField(
        ShortTermMemory,
        blank=True,
        related_name="derived_memories"
    )
    # どの会話から生成されたか

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.memory_type}"