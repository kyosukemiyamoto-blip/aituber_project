js/
├─ app.js
│   └─ アプリ全体の進行管理
│
├─ aituber_vtube_bridge.js
│   └─ app.jsとVTube Studioを仲介
│
├─ vtube_studio.js
│   └─ WebSocket・認証・VTube Studio API通信
│
├─ api_client.js        後で分離
├─ event_queue.js       後で分離
├─ comment_ui.js        後で分離
└─ audio_player.js      後で分離


app.js
  初期化
  DOMイベント登録
  キューへの処理追加

avatar_actions.js
  各API処理の流れ

api_client.js
  fetch通信とHTTPエラー処理

event_queue.js
  優先度付きキューの管理と順次実行

comment_ui.js
  コメント画面の描画

avatar_player.js
  音声再生、表情、リップシンク、音声削除

aituber_vtube_bridge.js
  app側とVTube Studio側の仲介

vtube_studio.js
  WebSocket、認証、VTube Studio API操作