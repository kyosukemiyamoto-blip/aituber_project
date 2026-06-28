import json
import os
import tempfile
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import User, ShortTermMemory, LongTermMemory

from .core.integrations.openai_utils import safe_json_parse
from .core.integrations.azure_utils import (
    convert_visemes_to_lip_sync,
    smooth_lip_sync,
)

from .core.utils.request_utils import parse_post_json

from .core.repositories.comment_store import (
    add_comment,
    add_reply,
    get_latest_comment,
    get_all_replies,
    comments,
    replies,
)
from .core.repositories.memory_repository import (
    add_ShortTermMemory,
    add_LongTermMemory,
    get_ShortTermMemory,
    get_LongTermMemory,
)

from .core.soul.history_builder import (
    format_short_term_memory,
    format_long_term_memory,
    format_long_term_memory_for_comparison,
)

from .core.services.conversation_service import generate_user_reply
from .core.services.memory_service import (
    create_long_term_memory_if_needed,
)
from .core.services.voice_service import (
    build_voice_reply,
    generate_voice_reply,
    delete_voice_file,
)
from .core.services.comment_service import create_generated_comment
from .core.services.comment_reply_service import create_comment_reply
from .core.services.user_comment_service import (
    create_user_comment_reply,
)
from .core.services.talk_service import (
    create_self_introduction_reply,
    create_news_talk_reply,
    create_weather_talk_reply,
)


# =========================================================
# Models
# =========================================================

class ModelTests(TestCase):
    def test_user_str_returns_username(self):
        user = User.objects.create(username="kyosuke")
        self.assertEqual(str(user), "kyosuke")

    def test_short_term_memory_str(self):
        user = User.objects.create(username="kyosuke")
        memory = ShortTermMemory.objects.create(
            user=user,
            role="user",
            content="こんにちは",
        )

        self.assertEqual(str(memory), "kyosuke: user")

    def test_long_term_memory_str(self):
        user = User.objects.create(username="kyosuke")
        memory = LongTermMemory.objects.create(
            user=user,
            memory_type="preference",
            content="猫が好き",
            importance=0.8,
        )

        self.assertEqual(str(memory), "kyosuke: preference")

    def test_long_term_memory_can_link_source_messages(self):
        user = User.objects.create(username="kyosuke")
        source = ShortTermMemory.objects.create(
            user=user,
            role="user",
            content="Pythonを勉強しています",
        )
        memory = LongTermMemory.objects.create(
            user=user,
            memory_type="skill",
            content="ユーザーはPythonを学習している",
            importance=0.8,
        )

        memory.source_messages.add(source)

        self.assertEqual(memory.source_messages.count(), 1)
        self.assertEqual(memory.source_messages.first(), source)


# =========================================================
# Utility functions
# =========================================================

class SafeJsonParseTests(TestCase):
    def test_valid_json_is_parsed(self):
        raw_text = '{"script": "こんにちは"}'
        fallback = {"script": "fallback"}

        result = safe_json_parse(raw_text, fallback)

        self.assertEqual(result, {"script": "こんにちは"})

    def test_invalid_json_returns_fallback(self):
        fallback = {"script": "fallback"}

        result = safe_json_parse("not-json", fallback)

        self.assertEqual(result, fallback)


class RequestUtilsTests(TestCase):
    def test_parse_post_json_accepts_valid_object(self):
        request = self.client.post(
            "/dummy/",
            data=json.dumps({"message": "hello"}),
            content_type="application/json",
        ).wsgi_request

        data, error = parse_post_json(request)

        self.assertEqual(data, {"message": "hello"})
        self.assertIsNone(error)

    def test_parse_post_json_rejects_non_post(self):
        request = self.client.get("/dummy/").wsgi_request

        data, error = parse_post_json(request)

        self.assertIsNone(data)
        self.assertEqual(error.status_code, 405)

    def test_parse_post_json_rejects_invalid_json(self):
        request = self.client.post(
            "/dummy/",
            data="not-json",
            content_type="application/json",
        ).wsgi_request

        data, error = parse_post_json(request)

        self.assertIsNone(data)
        self.assertEqual(error.status_code, 400)

    def test_parse_post_json_rejects_non_object_json(self):
        request = self.client.post(
            "/dummy/",
            data=json.dumps(["hello"]),
            content_type="application/json",
        ).wsgi_request

        data, error = parse_post_json(request)

        self.assertIsNone(data)
        self.assertEqual(error.status_code, 400)


class CommentStoreTests(TestCase):
    def setUp(self):
        comments.clear()
        replies.clear()

    def tearDown(self):
        comments.clear()
        replies.clear()

    def test_add_comment_and_get_latest_comment(self):
        first = {"username": "a", "text": "first"}
        second = {"username": "b", "text": "second"}

        add_comment(first)
        add_comment(second)

        self.assertEqual(get_latest_comment(), second)

    def test_get_latest_comment_returns_none_when_empty(self):
        self.assertIsNone(get_latest_comment())

    def test_comment_store_keeps_only_latest_30(self):
        for i in range(31):
            add_comment(
                {
                    "username": "user",
                    "text": str(i),
                }
            )

        self.assertEqual(len(comments), 30)
        self.assertEqual(comments[0]["text"], "1")
        self.assertEqual(comments[-1]["text"], "30")

    def test_reply_store_keeps_only_latest_30(self):
        for i in range(31):
            add_reply({"script": str(i)})

        self.assertEqual(len(get_all_replies()), 30)
        self.assertEqual(
            get_all_replies()[0]["script"],
            "1",
        )
        self.assertEqual(
            get_all_replies()[-1]["script"],
            "30",
        )


class HistoryBuilderTests(TestCase):
    def test_format_short_term_memory_without_history(self):
        result = format_short_term_memory(
            [],
            "kyosuke",
        )

        self.assertIn("初めて", result)
        self.assertIn(
            "過去の文脈はありません",
            result,
        )

    def test_format_short_term_memory_with_history(self):
        history = [
            {
                "role": "user",
                "content": "こんにちは",
            },
            {
                "role": "assistant",
                "content": "こんばんは",
            },
        ]

        result = format_short_term_memory(
            history,
            "kyosuke",
        )

        self.assertIn(
            "ユーザー: こんにちは",
            result,
        )
        self.assertIn(
            "人間猫: こんばんは",
            result,
        )

    def test_format_long_term_memory_without_memories(self):
        result = format_long_term_memory(
            [],
            "kyosuke",
        )

        self.assertIn(
            "長期記憶はまだありません",
            result,
        )

    def test_format_long_term_memory_with_memories(self):
        memories = [
            {
                "memory_type": "preference",
                "content": "猫が好き",
                "importance": 0.8,
            }
        ]

        result = format_long_term_memory(
            memories,
            "kyosuke",
        )

        self.assertIn("preference", result)
        self.assertIn("猫が好き", result)
        self.assertIn("0.8", result)

    def test_format_long_term_memory_for_comparison(self):
        memories = [
            {
                "memory_type": "skill",
                "content": "Pythonを学習している",
                "importance": 0.7,
            }
        ]

        result = format_long_term_memory_for_comparison(
            memories,
            "kyosuke",
        )

        self.assertIn(
            "既存の長期記憶",
            result,
        )
        self.assertIn(
            "Pythonを学習している",
            result,
        )


class MemoryRepositoryTests(TestCase):
    def test_add_short_term_memory_creates_two_messages(self):
        user_msg, assistant_msg = add_ShortTermMemory(
            "kyosuke",
            "こんにちは",
            "こんばんは",
        )

        self.assertEqual(user_msg.role, "user")
        self.assertEqual(
            user_msg.content,
            "こんにちは",
        )
        self.assertEqual(
            assistant_msg.role,
            "assistant",
        )
        self.assertEqual(
            assistant_msg.content,
            "こんばんは",
        )
        self.assertEqual(
            ShortTermMemory.objects.count(),
            2,
        )

    def test_get_short_term_memory_returns_latest_10_in_chronological_order(
        self,
    ):
        user = User.objects.create(
            username="kyosuke",
        )

        for i in range(12):
            ShortTermMemory.objects.create(
                user=user,
                role="user",
                content=str(i),
            )

        result = get_ShortTermMemory(
            "kyosuke",
        )

        self.assertEqual(len(result), 10)
        self.assertEqual(
            result[0]["content"],
            "2",
        )
        self.assertEqual(
            result[-1]["content"],
            "11",
        )

    def test_get_short_term_memory_returns_empty_for_unknown_user(
        self,
    ):
        self.assertEqual(
            get_ShortTermMemory("unknown"),
            [],
        )

    def test_add_long_term_memory_with_source(self):
        user_msg, _ = add_ShortTermMemory(
            "kyosuke",
            "Pythonを勉強している",
            "いいですね",
        )

        memory = add_LongTermMemory(
            "kyosuke",
            "skill",
            "ユーザーはPythonを学習している",
            0.8,
            [user_msg],
        )

        self.assertEqual(
            memory.memory_type,
            "skill",
        )
        self.assertEqual(
            memory.source_messages.count(),
            1,
        )

    def test_get_long_term_memory_is_sorted_by_importance(
        self,
    ):
        add_LongTermMemory(
            "kyosuke",
            "fact",
            "低重要度",
            0.6,
        )
        add_LongTermMemory(
            "kyosuke",
            "preference",
            "高重要度",
            0.9,
        )

        result = get_LongTermMemory(
            "kyosuke",
        )

        self.assertEqual(
            result[0]["content"],
            "高重要度",
        )
        self.assertEqual(
            result[1]["content"],
            "低重要度",
        )

    def test_get_long_term_memory_returns_empty_for_unknown_user(
        self,
    ):
        self.assertEqual(
            get_LongTermMemory("unknown"),
            [],
        )


class LipSyncTests(TestCase):
    def test_convert_visemes_to_lip_sync_returns_empty_for_empty_input(
        self,
    ):
        self.assertEqual(
            convert_visemes_to_lip_sync([]),
            [],
        )

    def test_convert_visemes_to_lip_sync_builds_durations(
        self,
    ):
        events = [
            {
                "offset": 0.0,
                "viseme_id": 1,
            },
            {
                "offset": 0.1,
                "viseme_id": 2,
            },
            {
                "offset": 0.25,
                "viseme_id": 3,
            },
        ]

        result = convert_visemes_to_lip_sync(
            events,
        )

        self.assertEqual(len(result), 3)
        self.assertEqual(
            result[0]["duration"],
            0.1,
        )
        self.assertEqual(
            result[1]["duration"],
            0.15,
        )
        self.assertEqual(
            result[2]["duration"],
            0.08,
        )

    def test_smooth_lip_sync_returns_short_list_unchanged(
        self,
    ):
        data = [
            {
                "mouth": 0.1,
                "duration": 0.1,
                "viseme_id": 1,
            },
            {
                "mouth": 0.9,
                "duration": 0.1,
                "viseme_id": 2,
            },
        ]

        self.assertEqual(
            smooth_lip_sync(data),
            data,
        )

    def test_smooth_lip_sync_smooths_middle_value(
        self,
    ):
        data = [
            {
                "mouth": 0.0,
                "duration": 0.1,
                "viseme_id": 1,
            },
            {
                "mouth": 1.0,
                "duration": 0.1,
                "viseme_id": 2,
            },
            {
                "mouth": 0.0,
                "duration": 0.1,
                "viseme_id": 3,
            },
        ]

        result = smooth_lip_sync(data)

        self.assertEqual(
            result[1]["mouth"],
            0.5,
        )


# =========================================================
# Services
# =========================================================

class ConversationServiceTests(TestCase):
    @patch(
        "avatar.core.services."
        "conversation_service.generate_character_reply"
    )
    def test_generate_user_reply_returns_ai_reply_without_saving_history(
        self,
        mock_generate,
    ):
        mock_generate.return_value = {
            "script": "こんにちは",
            "emotion": "happy",
        }

        result = generate_user_reply(
            username="kyosuke",
            user_message="やあ",
        )

        self.assertEqual(
            result["script"],
            "こんにちは",
        )
        self.assertEqual(
            result["emotion"],
            "happy",
        )
        self.assertIn(
            "long_term_memories",
            result,
        )
        self.assertEqual(
            ShortTermMemory.objects.count(),
            0,
        )

    @patch(
        "avatar.core.services."
        "conversation_service.generate_character_reply"
    )
    def test_generate_user_reply_raises_when_script_is_empty(
        self,
        mock_generate,
    ):
        mock_generate.return_value = {
            "script": "",
            "emotion": "normal",
        }

        with self.assertRaises(ValueError):
            generate_user_reply(
                username="kyosuke",
                user_message="やあ",
            )


class MemoryServiceTests(TestCase):
    @patch(
        "avatar.core.services."
        "memory_service.generate_LongTermMemory"
    )
    def test_create_long_term_memory_saves_valid_memory(
        self,
        mock_generate,
    ):
        mock_generate.return_value = {
            "memory_type": "skill",
            "content": "ユーザーはPythonを学習している",
            "importance": 0.8,
        }

        user_msg, _ = add_ShortTermMemory(
            "kyosuke",
            "Pythonを勉強しています",
            "いいですね",
        )

        result = create_long_term_memory_if_needed(
            username="kyosuke",
            user_message="Pythonを勉強しています",
            existing_memories=[],
            source_messages=[user_msg],
        )

        self.assertIsNotNone(result)
        self.assertEqual(
            LongTermMemory.objects.count(),
            1,
        )
        self.assertEqual(
            result.memory_type,
            "skill",
        )
        self.assertEqual(
            result.source_messages.first(),
            user_msg,
        )

    @patch(
        "avatar.core.services."
        "memory_service.generate_LongTermMemory"
    )
    def test_create_long_term_memory_ignores_none_type(
        self,
        mock_generate,
    ):
        mock_generate.return_value = {
            "memory_type": "none",
            "content": "",
            "importance": 0.0,
        }

        result = create_long_term_memory_if_needed(
            username="kyosuke",
            user_message="こんにちは",
            existing_memories=[],
            source_messages=[],
        )

        self.assertIsNone(result)
        self.assertEqual(
            LongTermMemory.objects.count(),
            0,
        )

    @patch(
        "avatar.core.services."
        "memory_service.generate_LongTermMemory"
    )
    def test_create_long_term_memory_ignores_low_importance(
        self,
        mock_generate,
    ):
        mock_generate.return_value = {
            "memory_type": "fact",
            "content": "一時的な情報",
            "importance": 0.5,
        }

        result = create_long_term_memory_if_needed(
            username="kyosuke",
            user_message="今日だけ眠い",
            existing_memories=[],
            source_messages=[],
        )

        self.assertIsNone(result)

    @patch(
        "avatar.core.services."
        "memory_service.generate_LongTermMemory"
    )
    def test_create_long_term_memory_ignores_invalid_type(
        self,
        mock_generate,
    ):
        mock_generate.return_value = {
            "memory_type": "invalid",
            "content": "不正な種類",
            "importance": 0.9,
        }

        result = create_long_term_memory_if_needed(
            username="kyosuke",
            user_message="test",
            existing_memories=[],
            source_messages=[],
        )

        self.assertIsNone(result)


class VoiceServiceTests(TestCase):
    @patch(
        "avatar.core.services."
        "voice_service.synthesize_for_vtube"
    )
    def test_build_voice_reply_combines_script_and_voice_data(
        self,
        mock_synthesize,
    ):
        mock_synthesize.return_value = {
            "audio_id": "voice.wav",
            "audio_url": "/media/voices/voice.wav",
            "lip_sync": [
                {
                    "mouth": 0.5,
                    "duration": 0.1,
                }
            ],
        }

        result = build_voice_reply(
            "こんにちは",
            "happy",
        )

        self.assertEqual(
            result["script"],
            "こんにちは",
        )
        self.assertEqual(
            result["emotion"],
            "happy",
        )
        self.assertEqual(
            result["audio_id"],
            "voice.wav",
        )

    @patch(
        "avatar.core.services."
        "voice_service.build_voice_reply"
    )
    def test_generate_voice_reply_calls_builders_and_generator(
        self,
        mock_build_voice_reply,
    ):
        mock_build_voice_reply.return_value = {
            "script": "こんにちは",
            "emotion": "normal",
        }

        instruction_builder = (
            lambda: "instruction"
        )
        input_builder = lambda: "input"
        generator = (
            lambda instruction, prompt_input: {
                "script": "こんにちは",
                "emotion": "normal",
            }
        )

        result = generate_voice_reply(
            instruction_builder,
            input_builder,
            generator,
        )

        self.assertEqual(
            result["script"],
            "こんにちは",
        )
        mock_build_voice_reply.assert_called_once_with(
            "こんにちは",
            "normal",
        )

    def test_generate_voice_reply_raises_when_script_is_empty(
        self,
    ):
        instruction_builder = (
            lambda: "instruction"
        )
        input_builder = lambda: "input"
        generator = (
            lambda instruction, prompt_input: {
                "script": "",
                "emotion": "normal",
            }
        )

        with self.assertRaises(ValueError):
            generate_voice_reply(
                instruction_builder,
                input_builder,
                generator,
            )

    def test_delete_voice_file_deletes_existing_file(
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            voice_dir = os.path.join(
                temp_dir,
                "voices",
            )
            os.makedirs(
                voice_dir,
                exist_ok=True,
            )

            file_path = os.path.join(
                voice_dir,
                "voice.wav",
            )
            with open(file_path, "wb") as file:
                file.write(b"test")

            with override_settings(
                MEDIA_ROOT=temp_dir,
            ):
                result = delete_voice_file(
                    "voice.wav",
                )

            self.assertTrue(
                result["deleted"],
            )
            self.assertFalse(
                os.path.exists(file_path),
            )

    def test_delete_voice_file_returns_not_found(
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(
                MEDIA_ROOT=temp_dir,
            ):
                result = delete_voice_file(
                    "missing.wav",
                )

            self.assertFalse(
                result["deleted"],
            )
            self.assertEqual(
                result["reason"],
                "file not found",
            )

    def test_delete_voice_file_uses_basename_for_safety(
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(
                MEDIA_ROOT=temp_dir,
            ):
                result = delete_voice_file(
                    "../../danger.wav",
                )

            self.assertEqual(
                result["audio_id"],
                "danger.wav",
            )


class CommentServiceTests(TestCase):
    def setUp(self):
        comments.clear()

    def tearDown(self):
        comments.clear()

    @patch(
        "avatar.core.services."
        "comment_service.generate_comment"
    )
    def test_create_generated_comment(
        self,
        mock_generate,
    ):
        mock_generate.return_value = {
            "username": "viewer1",
            "comment": "こんばんは",
        }

        result = create_generated_comment()

        self.assertEqual(
            result["comment"]["username"],
            "viewer1",
        )
        self.assertEqual(
            result["comment"]["text"],
            "こんばんは",
        )
        self.assertEqual(
            len(result["comments"]),
            1,
        )


class CommentReplyServiceTests(TestCase):
    def setUp(self):
        replies.clear()

    def tearDown(self):
        replies.clear()

    @patch(
        "avatar.core.services."
        "comment_reply_service.build_voice_reply"
    )
    @patch(
        "avatar.core.services."
        "comment_reply_service.generate_user_reply"
    )
    def test_create_comment_reply_saves_history_and_reply(
        self,
        mock_generate,
        mock_build_voice,
    ):
        mock_generate.return_value = {
            "script": "返信です",
            "emotion": "normal",
            "long_term_memories": [],
        }
        mock_build_voice.return_value = {
            "script": "返信です",
            "emotion": "normal",
            "audio_id": "voice.wav",
            "audio_url": "/media/voices/voice.wav",
            "lip_sync": [],
        }

        latest_comment = {
            "username": "viewer1",
            "text": "こんにちは",
            "time": "now",
        }

        result = create_comment_reply(
            latest_comment,
        )

        self.assertEqual(
            result["reply"]["target_comment"],
            latest_comment,
        )
        self.assertEqual(
            ShortTermMemory.objects.count(),
            2,
        )
        self.assertEqual(
            len(result["replies"]),
            1,
        )


class UserCommentServiceTests(TestCase):
    @patch(
        "avatar.core.services."
        "user_comment_service."
        "create_long_term_memory_if_needed"
    )
    @patch(
        "avatar.core.services."
        "user_comment_service.build_voice_reply"
    )
    @patch(
        "avatar.core.services."
        "user_comment_service.generate_user_reply"
    )
    def test_create_user_comment_reply_runs_full_flow(
        self,
        mock_generate,
        mock_build_voice,
        mock_create_memory,
    ):
        mock_generate.return_value = {
            "script": "返信です",
            "emotion": "happy",
            "long_term_memories": [],
        }
        mock_build_voice.return_value = {
            "script": "返信です",
            "emotion": "happy",
            "audio_id": "voice.wav",
            "audio_url": "/media/voices/voice.wav",
            "lip_sync": [],
        }

        result = create_user_comment_reply(
            "kyosuke",
            "Pythonを勉強しています",
        )

        self.assertEqual(
            result["script"],
            "返信です",
        )
        self.assertEqual(
            ShortTermMemory.objects.count(),
            2,
        )

        user_message = (
            ShortTermMemory.objects.get(
                role="user",
            )
        )

        mock_create_memory.assert_called_once_with(
            username="kyosuke",
            user_message="Pythonを勉強しています",
            existing_memories=[],
            source_messages=[user_message],
        )


class TalkServiceTests(TestCase):
    @patch(
        "avatar.core.services."
        "talk_service.generate_voice_reply"
    )
    def test_create_self_introduction_reply(
        self,
        mock_generate_voice_reply,
    ):
        mock_generate_voice_reply.return_value = {
            "script": "自己紹介",
            "emotion": "normal",
        }

        result = create_self_introduction_reply()

        self.assertEqual(
            result["script"],
            "自己紹介",
        )
        mock_generate_voice_reply.assert_called_once()

    @patch(
        "avatar.core.services."
        "talk_service.generate_voice_reply"
    )
    def test_create_news_talk_reply(
        self,
        mock_generate_voice_reply,
    ):
        mock_generate_voice_reply.return_value = {
            "script": "ニュース",
            "emotion": "surprised",
        }

        result = create_news_talk_reply()

        self.assertEqual(
            result["script"],
            "ニュース",
        )

    @patch(
        "avatar.core.services."
        "talk_service.generate_voice_reply"
    )
    def test_create_weather_talk_reply(
        self,
        mock_generate_voice_reply,
    ):
        mock_generate_voice_reply.return_value = {
            "script": "天気",
            "emotion": "normal",
        }

        result = create_weather_talk_reply()

        self.assertEqual(
            result["script"],
            "天気",
        )


# =========================================================
# API / Views
# =========================================================

class ApiViewTests(TestCase):
    def setUp(self):
        comments.clear()
        replies.clear()

    def tearDown(self):
        comments.clear()
        replies.clear()

    def test_index_returns_200(self):
        response = self.client.get(
            reverse("index"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    @patch(
        "avatar.views.create_generated_comment"
    )
    def test_generate_comment_api(
        self,
        mock_create,
    ):
        mock_create.return_value = {
            "comment": {
                "username": "viewer",
                "text": "こんにちは",
                "time": "now",
            },
            "comments": [],
        }

        response = self.client.get(
            reverse("generate_comment_api"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.json()["comment"]["text"],
            "こんにちは",
        )

    def test_reply_to_comment_api_returns_400_when_no_comment(
        self,
    ):
        response = self.client.get(
            reverse("reply_to_comment_api"),
        )

        self.assertEqual(
            response.status_code,
            400,
        )
        self.assertEqual(
            response.json()["code"],
            "COMMENT_NOT_FOUND",
        )

    @patch(
        "avatar.views.create_comment_reply"
    )
    def test_reply_to_comment_api(
        self,
        mock_create,
    ):
        add_comment(
            {
                "username": "viewer",
                "text": "こんにちは",
                "time": "now",
            }
        )
        mock_create.return_value = {
            "reply": {
                "script": "返信",
            },
            "replies": [],
        }

        response = self.client.get(
            reverse("reply_to_comment_api"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.json()["reply"]["script"],
            "返信",
        )

    @patch(
        "avatar.views.create_self_introduction_reply"
    )
    def test_self_introduction_api(
        self,
        mock_create,
    ):
        mock_create.return_value = {
            "script": "自己紹介",
            "emotion": "normal",
        }

        response = self.client.get(
            reverse("self_introduction_api"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.json()["reply"]["script"],
            "自己紹介",
        )

    @patch(
        "avatar.views.create_news_talk_reply"
    )
    def test_news_talk_api(
        self,
        mock_create,
    ):
        mock_create.return_value = {
            "script": "ニュース",
            "emotion": "normal",
        }

        response = self.client.get(
            reverse("news_talk_api"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.json()["reply"]["script"],
            "ニュース",
        )

    @patch(
        "avatar.views.create_weather_talk_reply"
    )
    def test_weather_talk_api(
        self,
        mock_create,
    ):
        mock_create.return_value = {
            "script": "天気",
            "emotion": "normal",
        }

        response = self.client.get(
            reverse("weather_talk_api"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.json()["reply"]["script"],
            "天気",
        )

    @patch(
        "avatar.views.create_user_comment_reply"
    )
    def test_user_comment_api(
        self,
        mock_create,
    ):
        mock_create.return_value = {
            "script": "返信",
            "emotion": "happy",
        }

        response = self.client.post(
            reverse("user_comment_api"),
            data=json.dumps(
                {
                    "username": "kyosuke",
                    "message": "こんにちは",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.json()["reply"]["script"],
            "返信",
        )

    def test_user_comment_api_rejects_get(self):
        response = self.client.get(
            reverse("user_comment_api"),
        )

        self.assertEqual(
            response.status_code,
            405,
        )
        self.assertEqual(
            response.json()["code"],
            "METHOD_NOT_ALLOWED",
        )

    def test_user_comment_api_rejects_invalid_json(
        self,
    ):
        response = self.client.post(
            reverse("user_comment_api"),
            data="not-json",
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )
        self.assertEqual(
            response.json()["code"],
            "INVALID_JSON",
        )

    def test_user_comment_api_requires_username_and_message(
        self,
    ):
        response = self.client.post(
            reverse("user_comment_api"),
            data=json.dumps(
                {
                    "username": "kyosuke",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )
        self.assertEqual(
            response.json()["code"],
            "INVALID_INPUT",
        )

    @patch(
        "avatar.views.delete_voice_file"
    )
    def test_delete_voice_api(
        self,
        mock_delete,
    ):
        mock_delete.return_value = {
            "deleted": True,
            "audio_id": "voice.wav",
        }

        response = self.client.post(
            reverse("delete_voice_api"),
            data=json.dumps(
                {
                    "audio_id": "voice.wav",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTrue(
            response.json()["deleted"],
        )

    def test_delete_voice_api_requires_audio_id(
        self,
    ):
        response = self.client.post(
            reverse("delete_voice_api"),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )
        self.assertEqual(
            response.json()["code"],
            "AUDIO_ID_REQUIRED",
        )

    @patch(
        "avatar.views.create_news_talk_reply"
    )
    def test_api_error_handler_returns_500(
        self,
        mock_create,
    ):
        mock_create.side_effect = RuntimeError(
            "test error",
        )

        response = self.client.get(
            reverse("news_talk_api"),
        )

        self.assertEqual(
            response.status_code,
            500,
        )
        self.assertEqual(
            response.json()["code"],
            "INTERNAL_SERVER_ERROR",
        )