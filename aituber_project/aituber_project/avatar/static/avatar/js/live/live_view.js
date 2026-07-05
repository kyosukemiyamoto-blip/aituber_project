function setBadgeState(ui, text, statusClass) {
    ui.liveStatusBadge.textContent = text;

    ui.liveStatusBadge.classList.remove(
        "connected",
        "disconnected"
    );

    if (statusClass) {
        ui.liveStatusBadge.classList.add(
            statusClass
        );
    }
}


export function resetLiveView(ui) {
    setBadgeState(
        ui,
        "接続準備中",
        "disconnected"
    );

    ui.liveTitleText.textContent = "-";
    ui.videoIdText.textContent = "-";
    ui.commentPollingStatus.textContent = "停止中";

    ui.startBroadcastBtn.disabled = true;
    ui.startBroadcastBtn.textContent = "配信開始";
    ui.stopLiveBtn.disabled = false;

    ui.currentCommentUsername.textContent = "-";
    ui.currentCommentTime.textContent = "-";
    ui.currentCommentText.textContent =
        "現在処理中のコメントはありません。";

    ui.replyProcessStatus.textContent = "待機中";
    ui.currentReplyText.textContent =
        "返信はまだ生成されていません。";
    ui.currentReplyEmotion.textContent = "-";
    ui.currentAudioStatus.textContent = "-";

    ui.queueCount.textContent = "0";
    clearSystemLog(ui);
}


export function showLiveInformation(ui, liveInfo) {
    ui.liveTitleText.textContent =
        liveInfo.title || "-";

    ui.videoIdText.textContent =
        liveInfo.videoId || "-";

    setBadgeState(
        ui,
        "コメント接続中",
        "disconnected"
    );

    ui.commentPollingStatus.textContent =
        "コメント取得開始中";

    ui.startBroadcastBtn.disabled = true;
    ui.startBroadcastBtn.textContent =
        "配信開始";
}


export function showMissingSetup(ui) {
    setBadgeState(
        ui,
        "接続情報なし",
        "disconnected"
    );

    ui.commentPollingStatus.textContent =
        "index画面から配信接続してください";

    ui.startBroadcastBtn.disabled = true;
    ui.stopLiveBtn.disabled = true;
}


export function showPollingStarted(ui) {
    ui.startBroadcastBtn.disabled = true;
    ui.commentPollingStatus.textContent =
        "コメント取得開始中";
}


export function showPollingReady(
    ui,
    broadcastStarted
) {
    ui.commentPollingStatus.textContent =
        "コメント取得中";

    setBadgeState(
        ui,
        broadcastStarted
            ? "配信中"
            : "配信開始待ち",
        "connected"
    );

    if (!broadcastStarted) {
        ui.startBroadcastBtn.disabled = false;
    }
}


export function showPollingStatus(ui, status) {
    ui.commentPollingStatus.textContent =
        status?.message || "コメント取得中";
}


export function showPollingError(
    ui,
    broadcastStarted
) {
    ui.commentPollingStatus.textContent =
        "コメント取得エラー・再試行中";

    if (!broadcastStarted) {
        setBadgeState(
            ui,
            "再接続中",
            "disconnected"
        );

        ui.startBroadcastBtn.disabled = true;
    }
}


export function showLiveEnded(ui) {
    setBadgeState(
        ui,
        "ライブ終了",
        "disconnected"
    );

    ui.commentPollingStatus.textContent =
        "YouTube Live終了";

    ui.startBroadcastBtn.disabled = true;
}


export function showBroadcastStarted(ui) {
    setBadgeState(
        ui,
        "配信中",
        "connected"
    );

    ui.startBroadcastBtn.disabled = true;
    ui.startBroadcastBtn.textContent =
        "配信中";
}


export function showLiveStopped(
    ui,
    broadcastStarted
) {
    setBadgeState(
        ui,
        "停止中",
        "disconnected"
    );

    ui.commentPollingStatus.textContent =
        "コメント取得停止";

    ui.startBroadcastBtn.disabled = true;

    if (!broadcastStarted) {
        ui.startBroadcastBtn.textContent =
            "配信開始";
    }
}


export function showIntroductionQueued(ui) {
    ui.queueCount.textContent = "1";
    ui.replyProcessStatus.textContent =
        "キュー待機中";
    ui.currentReplyText.textContent =
        "自己紹介を開始します。";
    ui.currentReplyEmotion.textContent = "-";
    ui.currentAudioStatus.textContent =
        "待機中";
}


export function showIntroductionProcessing(ui) {
    ui.queueCount.textContent = "0";
    ui.replyProcessStatus.textContent =
        "自己紹介処理中";
    ui.currentReplyText.textContent =
        "自己紹介を生成・再生しています。";
    ui.currentAudioStatus.textContent =
        "生成・再生中";
}


export function showIntroductionCompleted(ui) {
    ui.replyProcessStatus.textContent =
        "待機中";
    ui.currentReplyText.textContent =
        "自己紹介処理を終了しました。";
    ui.currentAudioStatus.textContent =
        "終了";
}


export function showIntroductionError(ui) {
    ui.replyProcessStatus.textContent =
        "エラー";
    ui.currentReplyText.textContent =
        "自己紹介処理でエラーが発生しました。";
    ui.currentAudioStatus.textContent =
        "エラー";
}


export function clearLiveComments(ui) {
    ui.commentList.innerHTML = "";

    const emptyMessage =
        document.createElement("p");

    emptyMessage.className =
        "empty_message";

    emptyMessage.textContent =
        "コメントはまだ取得されていません。";

    ui.commentList.appendChild(
        emptyMessage
    );
}


export function clearSystemLog(ui) {
    ui.systemLog.innerHTML = "";
}


export function writeSystemLog(
    ui,
    message,
    type = "info"
) {
    const item =
        document.createElement("p");

    item.className =
        `log_item ${type}`;

    const time =
        new Date().toLocaleTimeString("ja-JP");

    item.textContent =
        `[${time}] ${message}`;

    ui.systemLog.appendChild(item);

    ui.systemLog.scrollTop =
        ui.systemLog.scrollHeight;
}
