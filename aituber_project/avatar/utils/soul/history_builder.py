def format_history(history, username):
    formatted_history = ""

    if history:
        for message in history:
            formatted_history += (
                f"{message['role']}: "
                f"{message['content']}\n"
            )

        history_instruction = f"""
ユーザー「{username}」とは以前やり取りしています。

直近履歴:
{formatted_history}

この流れを踏まえて自然に返信してください。
"""
    else:
        history_instruction = (
            f"ユーザー「{username}」がコメントしたのは初めてです。"
        )

    return history_instruction