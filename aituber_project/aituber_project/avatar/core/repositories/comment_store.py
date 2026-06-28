comments = []
replies = []


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