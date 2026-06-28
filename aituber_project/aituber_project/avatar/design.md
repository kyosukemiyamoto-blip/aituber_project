views        HTTPを受け取って返す
services     一連の処理を組み立てる
repositories DBへの保存・取得
clients      外部APIとの通信
prompts      AIに渡す文章を作る
utils        汎用処理
models       DB構造

avatar/
├── migrations/
├── templates/
├── static/
│
├── models.py
├── urls.py
│
├── views/
│   ├── __init__.py
│   ├── page_views.py
│   ├── comment_views.py
│   ├── talk_views.py
│   └── voice_views.py
│
├── services/
│   ├── __init__.py
│   ├── comment_service.py
│   ├── conversation_service.py
│   ├── talk_service.py
│   ├── memory_service.py
│   └── voice_service.py
│
├── repositories/
│   ├── __init__.py
│   ├── memory_repository.py
│   └── comment_repository.py
│
├── clients/
│   ├── __init__.py
│   ├── openai_client.py
│   ├── azure_speech_client.py
│   └── elevenlabs_client.py
│
├── prompts/
│   ├── __init__.py
│   ├── character.py
│   ├── comment.py
│   ├── talk.py
│   ├── memory.py
│   ├── input_builder.py
│   └── history_formatter.py
│
├── utils/
│   ├── __init__.py
│   ├── api_errors.py
│   ├── request_parser.py
│   └── json_parser.py
│
└── tests/
    ├── test_views.py
    ├── test_services.py
    ├── test_memory_service.py
    └── test_prompt_builders.py