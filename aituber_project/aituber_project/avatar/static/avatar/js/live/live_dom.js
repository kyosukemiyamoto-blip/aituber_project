function getRequiredElement(id) {
    const element = document.getElementById(id);

    if (!element) {
        throw new Error(`必須DOMが見つかりません: #${id}`);
    }

    return element;
}


export function getLiveElements() {
    return {
        // Live状態
        liveStatusBadge:
            getRequiredElement("liveStatusBadge"),

        startBroadcastBtn:
            getRequiredElement("startBroadcastBtn"),

        stopLiveBtn:
            getRequiredElement("stopLiveBtn"),

        // Live情報
        liveTitleText:
            getRequiredElement("liveTitleText"),

        videoIdText:
            getRequiredElement("videoIdText"),

        commentPollingStatus:
            getRequiredElement("commentPollingStatus"),

        // 現在処理中のコメント
        currentCommentUsername:
            getRequiredElement("currentCommentUsername"),

        currentCommentTime:
            getRequiredElement("currentCommentTime"),

        currentCommentText:
            getRequiredElement("currentCommentText"),

        // 現在の返信
        replyProcessStatus:
            getRequiredElement("replyProcessStatus"),

        currentReplyText:
            getRequiredElement("currentReplyText"),

        currentReplyEmotion:
            getRequiredElement("currentReplyEmotion"),

        currentAudioStatus:
            getRequiredElement("currentAudioStatus"),

        // イベントキュー
        queueCount:
            getRequiredElement("queueCount"),

        eventQueue:
            getRequiredElement("eventQueue"),

        // コメント一覧
        commentList:
            getRequiredElement("liveCommentList"),

        clearCommentsBtn:
            getRequiredElement("clearCommentsBtn"),

        // システムログ
        systemLog:
            getRequiredElement("systemLog"),

        clearLogBtn:
            getRequiredElement("clearLogBtn")
    };
}
