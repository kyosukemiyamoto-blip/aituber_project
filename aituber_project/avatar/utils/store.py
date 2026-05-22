comments = []
replies = []
from avatar.models import (
    User,
    ShortTermMemory
)
def add_user_history(username: str, comment: str, reply: str):
    user, created = User.objects.get_or_create(username=username)
    ShortTermMemory.objects.create(user=user,role="user",content=comment)
    ShortTermMemory.objects.create(user=user,role="assistant",content=reply)



def get_user_history(username: str):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return []

    messages = (ShortTermMemory.objects.filter(user=user).order_by("-created_at")[:20])
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