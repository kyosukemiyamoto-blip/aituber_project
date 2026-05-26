comments = []
replies = []
from avatar.models import (
    User,
    ShortTermMemory,
    LongTermMemory
)

def add_LongTermMemory(username: str, memory_type: str, content: str, importance: float, source_messages=None):
    user, created = User.objects.get_or_create(username=username)
    ltm = LongTermMemory.objects.create(user=user,memory_type=memory_type,content=content,importance=importance)

    if source_messages:
        ltm.source_messages.add(*source_messages)

    return ltm


def add_ShortTermMemory(username: str, comment: str, reply: str):
    user, created = User.objects.get_or_create(username=username)
    user_msg = ShortTermMemory.objects.create(user=user,role="user",content=comment)
    assistant_reply = ShortTermMemory.objects.create(user=user,role="assistant",content=reply)
    
    return user_msg, assistant_reply

def get_LongTermMemory(username: str):
    try:
        user = User.objects.get(username=username)
    except:
        return []

    memories = LongTermMemory.objects.filter(user=user).order_by("-importance", "-created_at")

    return [
        {
            "memory_type": m.memory_type,
            "content": m.content,
            "importance": m.importance,
        }
        for m in memories
    ]


def get_ShortTermMemory(username: str):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return []

    messages = (ShortTermMemory.objects.filter(user=user).order_by("-created_at")[:10])
    messages = reversed(messages)

    return [{"role": message.role, "content": message.content} for message in messages]




def add_comment(comment_data: dict):
    comments.append(comment_data)

    if len(comments) > 30:
        comments.pop(0)

    return comments


def add_reply(reply_data: dict):
    replies.append(reply_data)

    if len(replies) > 30:
        replies.pop(0)

    return replies


def get_latest_comment():
    if not comments:
        return None

    return comments[-1]



def get_all_replies():
    return replies