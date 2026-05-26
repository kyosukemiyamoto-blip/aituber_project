def format_history(history, username):
    if not history:
        return f"""
ユーザー「{username}」がコメントしたのは初めてです。
過去の文脈はありません。
"""

    formatted_history = ""

    for message in history:
        role = message["role"]
        content = message["content"]

        if role == "user":
            formatted_history += f"ユーザー: {content}\n"
        elif role == "assistant":
            formatted_history += f"人間猫: {content}\n"

    return f"""
ユーザー「{username}」とは以前やり取りしています。

【直近の会話履歴】
{formatted_history}

【履歴の扱い】
- この履歴は、同じユーザーとの直近の会話文脈です。
- ユーザーの過去発言は、今回の返信に必要な場合だけ参考にしてください。
- 人間猫の過去発言は、会話の流れを理解するためだけに使ってください。
- 人間猫の過去発言を、ユーザー本人の情報として扱ってはいけません。
- 最新コメントへの返信を最優先してください。
"""