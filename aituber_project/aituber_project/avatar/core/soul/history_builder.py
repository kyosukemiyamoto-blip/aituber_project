def format_short_term_memory(history, username):
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


#------------------------------------------------------------------------------------------------------------------------------------

def format_long_term_memory(memories, username):
    if not memories:
        return f"""
ユーザー「{username}」に関する長期記憶はまだありません。
"""

    formatted_memory = ""

    for memory in memories:
        memory_type = memory["memory_type"]
        content = memory["content"]
        importance = memory["importance"]

        formatted_memory += (
            f"- 種類: {memory_type}\n"
            f"  内容: {content}\n"
            f"  重要度: {importance}\n"
        )

    return f"""
【ユーザー「{username}」に関する長期記憶】
{formatted_memory}

【長期記憶の扱い】
- これはユーザー本人に関する継続的な情報です。
- 最新コメントに関係する場合だけ自然に参考にしてください。
- 無理に長期記憶の内容を説明しないでください。
- 「覚えているよ」を毎回使わないでください。
- 最新コメントへの返信を最優先してください。
"""

def format_long_term_memory_for_comparison(memories, username):
    if not memories:
        return f"""
【既存の長期記憶】
ユーザー「{username}」に関する長期記憶はまだありません。
"""

    formatted_memory = ""

    for memory in memories:
        memory_type = memory["memory_type"]
        content = memory["content"]
        importance = memory["importance"]

        formatted_memory += (
            f"- 種類: {memory_type}\n"
            f"  内容: {content}\n"
            f"  重要度: {importance}\n"
        )

    return f"""
【既存の長期記憶】
以下はすでに保存されている記憶です。
新しい記憶候補との重複判定にのみ使用してください。

{formatted_memory}
"""