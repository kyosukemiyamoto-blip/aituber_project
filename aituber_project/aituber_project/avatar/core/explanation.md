services
→ 処理の流れ

repositories
→ データ保存・取得

integrations
→ 外部API接続

soul
→ AIの人格・プロンプト

utils
→ 小さな共通処理


#services/
1. 機能全体の処理手順をまとめる場所です

AIで文章を作る
記憶を取得する
音声を生成する
保存する
最終的な返却データを作る

といった複数の処理を組み合わせます。

要するに、

「何を、どの順番で実行するか」


#repositories/
2. データの保存と取得を担当する場所です。

対象は、
Djangoのデータベース
Pythonのリスト
将来的にはRedisや外部DB
などです。


#integrations/

3. 外部サービスとの接続を担当する場所です。
今回なら、
OpenAI API
Azure Speech
将来的なニュースAPI
天気API
ElevenLabs
などが該当します。




#soul/

4. AIの人格やプロンプトを作る場所です。
ここには、
キャラクター設定
AIへの指示
ユーザー入力の整形
会話履歴の整形
JSON出力ルール
などを置きます。