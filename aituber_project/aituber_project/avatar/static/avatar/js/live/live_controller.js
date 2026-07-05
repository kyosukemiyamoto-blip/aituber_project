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


/**
 * Liveページ全体を初期化する。
 */
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


/**
 * 外部モジュールへ画面上の表示先を渡す。
 */
function initializeDependencies() {
    initializeVTubeStudioBridge();
    initializeCommentUI(ui.commentList);
    initializeEventQueue(ui.eventQueue);
}


/**
 * Live画面のボタンイベントを登録する。
 */
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


/**
 * YouTube LiveコメントPollingを開始する。
 */
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


/**
 * 新着コメントを画面へ追加する。
 */
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


/**
 * Polling状態を画面へ反映する。
 */
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


/**
 * Pollingエラーを処理する。
 */
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


/**
 * YouTube Live終了時の状態を反映する。
 */
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


/**
 * AITuberの配信処理を開始する。
 */
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


/**
 * 自己紹介をイベントキューへ追加する。
 */
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


/**
 * 自己紹介生成・再生を実行する。
 */
async function runSelfIntroduction() {
    showIntroductionProcessing(ui);

    writeSystemLog(
        ui,
        "自己紹介処理を開始しました"
    );

    try {
        await generateSelfIntroduction();

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


/**
 * Pollingと自動処理を停止する。
 */
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


/**
 * ページ離脱時にPollingを停止する。
 */
export function destroyLivePage() {
    stopYouTubeLiveCommentPolling();
}
