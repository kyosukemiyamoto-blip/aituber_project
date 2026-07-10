import {
    initializeVTubeStudioBridge
} from "../core/aituber_vtube_bridge.js";

import {
    initializeEventQueue,
    enqueueEvent
} from "../core/event_queue.js";

import {
    initializeCommentUI,
    addCommentsToUI
} from "../core/comment_ui.js";

import {
    generateSelfIntroduction
} from "../core/avatar_actions.js";

import {
    startYouTubeLiveCommentPolling,
    stopYouTubeLiveCommentPolling
} from "./youtube_live_api.js";

import {
    liveState,
    resetLiveState
} from "./live_state.js";

import {
    getLiveElements
} from "./live_dom.js";

import {
    loadLiveSetupData
} from "./live_storage.js";

import {
    resetLiveView,
    showLiveInformation,
    showMissingSetup,
    showPollingStarted,
    showPollingReady,
    showPollingStatus,
    showPollingError,
    showLiveEnded,
    showBroadcastStarted,
    showLiveStopped,
    showIntroductionQueued,
    showIntroductionProcessing,
    showIntroductionCompleted,
    showIntroductionError,
    clearLiveComments,
    clearSystemLog,
    writeSystemLog
} from "./live_view.js";


let ui = null;



export function initializeLivePage() {
    if (liveState.initialized) {
        return;
    }

    ui = getLiveElements();

    initializeDependencies();
    resetLiveState();
    resetLiveView(ui);
    bindLiveEvents();

    const liveInfo = loadLiveSetupData();

    if (!liveInfo) {
        showMissingSetup(ui);

        writeSystemLog(
            ui,
            "配信接続情報がありません。index画面から配信接続してください。",
            "error"
        );

        return;
    }

    liveState.liveInfo = liveInfo;
    liveState.initialized = true;

    showLiveInformation(ui, liveInfo);

    writeSystemLog(
        ui,
        `配信接続情報を読み込みました: ${
            liveInfo.title || liveInfo.videoId
        }`
    );

    startCommentPolling();
}



function initializeDependencies() {
    initializeVTubeStudioBridge();
    initializeCommentUI(ui.commentList);
    initializeEventQueue(ui.eventQueue);
}


function bindLiveEvents() {
    ui.startBroadcastBtn.addEventListener(
        "click",
        startBroadcast
    );

    ui.stopLiveBtn.addEventListener(
        "click",
        stopLiveSession
    );

    ui.clearCommentsBtn.addEventListener(
        "click",
        handleClearComments
    );

    ui.clearLogBtn.addEventListener(
        "click",
        () => clearSystemLog(ui)
    );
}


function handleClearComments() {
    clearLiveComments(ui);

    writeSystemLog(
        ui,
        "コメント履歴を削除しました"
    );
}



function startCommentPolling() {
    const liveChatId =
        liveState.liveInfo?.liveChatId;

    if (!liveChatId) {
        showMissingSetup(ui);
        return;
    }

    if (liveState.pollingStarted) {
        return;
    }

    liveState.pollingStarted = true;
    liveState.pollingReady = false;
    liveState.liveEnded = false;

    showPollingStarted(ui);

    writeSystemLog(
        ui,
        "YouTube Liveコメント取得を開始します"
    );

    startYouTubeLiveCommentPolling({
        liveChatId,
        onComments: handleReceivedComments,
        onStatus: handlePollingStatus,
        onError: handlePollingError,
        onLiveEnd: handleLiveEnd
    });
}



function handleReceivedComments(comments) {
    if (
        !Array.isArray(comments) ||
        comments.length === 0
    ) {
        return;
    }

    addCommentsToUI(comments);

    writeSystemLog(
        ui,
        `新着コメントを${comments.length}件取得しました`
    );
}




function handlePollingStatus(status) {
    showPollingStatus(ui, status);

    if (status?.status !== "polling") {
        return;
    }

    if (liveState.pollingReady) {
        return;
    }

    liveState.pollingReady = true;

    showPollingReady(
        ui,
        liveState.broadcastStarted
    );

    writeSystemLog(
        ui,
        "コメント接続が完了しました。配信開始できます。"
    );
}



function handlePollingError(error) {
    console.error(
        "YouTube Liveコメント取得エラー:",
        error
    );

    if (!liveState.broadcastStarted) {
        liveState.pollingReady = false;
    }

    showPollingError(
        ui,
        liveState.broadcastStarted
    );

    writeSystemLog(
        ui,
        `コメント取得エラー: ${
            error?.message || "不明なエラー"
        }`,
        "error"
    );
}



function handleLiveEnd(data) {
    liveState.pollingStarted = false;
    liveState.pollingReady = false;
    liveState.liveEnded = true;

    showLiveEnded(ui);

    const offlineAt =
        data?.offlineAt
            ? `: ${data.offlineAt}`
            : "";

    writeSystemLog(
        ui,
        `YouTube Liveが終了しました${offlineAt}`
    );
}




function startBroadcast() {
    if (liveState.broadcastStarted) {
        return;
    }

    if (liveState.liveEnded) {
        writeSystemLog(
            ui,
            "終了済みのライブでは配信開始できません",
            "error"
        );

        return;
    }

    if (!liveState.pollingReady) {
        writeSystemLog(
            ui,
            "コメント接続が完了していません",
            "error"
        );

        return;
    }

    liveState.broadcastStarted = true;

    showBroadcastStarted(ui);

    writeSystemLog(
        ui,
        "配信を開始しました"
    );

    enqueueSelfIntroduction();
}




function enqueueSelfIntroduction() {
    showIntroductionQueued(ui);

    enqueueEvent(
        "self_introduction",
        100,
        runSelfIntroduction
    );

    writeSystemLog(
        ui,
        "自己紹介をイベントキューへ追加しました"
    );
}




async function runSelfIntroduction() {
    showIntroductionProcessing(ui);

    writeSystemLog(
        ui,
        "自己紹介処理を開始しました"
    );

    try {
        await generateSelfIntroduction(ui);

        showIntroductionCompleted(ui);

        writeSystemLog(
            ui,
            "自己紹介処理を終了しました"
        );

    } catch (error) {
        console.error(
            "自己紹介処理エラー:",
            error
        );

        showIntroductionError(ui);

        writeSystemLog(
            ui,
            `自己紹介処理エラー: ${
                error?.message ||
                "不明なエラー"
            }`,
            "error"
        );

        throw error;
    }
}




function stopLiveSession() {
    stopYouTubeLiveCommentPolling();

    liveState.pollingStarted = false;
    liveState.pollingReady = false;

    showLiveStopped(
        ui,
        liveState.broadcastStarted
    );

    writeSystemLog(
        ui,
        "コメント取得と自動処理を停止しました"
    );
}



export function destroyLivePage() {
    stopYouTubeLiveCommentPolling();
}
