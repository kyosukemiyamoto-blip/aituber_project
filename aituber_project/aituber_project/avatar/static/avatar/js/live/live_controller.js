import {
    initializeVTubeStudioBridge
} from "../core/aituber_vtube_bridge.js";

import {
    initializeEventQueue,
    enqueueEvent,
    clearEventQueue,
    isEventQueueIdle
} from "../core/event_queue.js";

import {
    initializeCommentUI,
    addCommentsToUI
} from "../core/comment_ui.js";

import {
    generateSelfIntroduction,
    generateNewsTalk,
    generateWeatherTalk,
    replyToLiveComment
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
    showQueueCount,
    showIntroductionQueued,
    showIntroductionProcessing,
    showIntroductionCompleted,
    showIntroductionError,
    showCommentProcessing,
    showCommentCompleted,
    showCommentError,
    showIdleTalkProcessing,
    showIdleTalkCompleted,
    showIdleTalkError,
    clearLiveComments,
    clearSystemLog,
    writeSystemLog
} from "./live_view.js";


const EVENT_PRIORITY = Object.freeze({
    SELF_INTRODUCTION: 100,
    LIVE_COMMENT: 80,
    IDLE_TALK: 10
});

const IDLE_TALK_DELAY_MS = 5000;

let ui = null;
let idleTalkTimerId = null;
let nextIdleTalkType = "news";

const receivedCommentKeys = new Set();


export function initializeLivePage() {
    if (liveState.initialized) {
        return;
    }

    ui = getLiveElements();

    resetLiveState();
    resetLiveView(ui);
    resetAutomationState();
    initializeDependencies();
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


function resetAutomationState() {
    cancelIdleTalkTimer();
    receivedCommentKeys.clear();
    nextIdleTalkType = "news";
}


function initializeDependencies() {
    initializeVTubeStudioBridge();
    initializeCommentUI(ui.commentList);

    initializeEventQueue(
        ui.eventQueue,
        {
            onChange: handleQueueChange,
            onIdle: handleQueueIdle
        }
    );
}


function handleQueueChange({ pendingCount }) {
    showQueueCount(
        ui,
        pendingCount
    );
}


function handleQueueIdle() {
    if (!canRunAutomaticBroadcast()) {
        return;
    }

    scheduleIdleTalk();
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

    for (const comment of comments) {
        const commentKey =
            createCommentKey(comment);

        const alreadyReceived =
            receivedCommentKeys.has(commentKey);

        receivedCommentKeys.add(commentKey);

        if (
            alreadyReceived ||
            !liveState.broadcastStarted
        ) {
            continue;
        }

        enqueueLiveComment(comment);
    }
}


function createCommentKey(comment) {
    if (comment?.id) {
        return String(comment.id);
    }

    return [
        comment?.username || "",
        comment?.text || "",
        comment?.time || ""
    ].join("\u0000");
}


function enqueueLiveComment(comment) {
    cancelIdleTalkTimer();

    const username =
        comment?.username || "unknown";

    enqueueEvent(
        `live_comment:${username}`,
        EVENT_PRIORITY.LIVE_COMMENT,
        () => runLiveCommentReply(comment)
    );

    writeSystemLog(
        ui,
        `${username} のコメント返信をキューへ追加しました`
    );
}


async function runLiveCommentReply(comment) {
    const username =
        comment?.username || "unknown";

    showCommentProcessing(
        ui,
        comment
    );

    writeSystemLog(
        ui,
        `${username} のコメント返信を開始しました`
    );

    try {
        await replyToLiveComment(
            comment,
            ui
        );

        showCommentCompleted(ui);

        writeSystemLog(
            ui,
            `${username} のコメント返信を終了しました`
        );

    } catch (error) {
        console.error(
            "Liveコメント返信処理エラー:",
            error
        );

        showCommentError(ui);

        writeSystemLog(
            ui,
            `コメント返信エラー: ${
                error?.message || "不明なエラー"
            }`,
            "error"
        );

        throw error;
    }
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
    liveState.broadcastStarted = false;
    liveState.liveEnded = true;

    cancelIdleTalkTimer();
    clearEventQueue();
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
    nextIdleTalkType = "news";

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
        EVENT_PRIORITY.SELF_INTRODUCTION,
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


function canRunAutomaticBroadcast() {
    return Boolean(
        liveState.broadcastStarted &&
        liveState.pollingStarted &&
        !liveState.liveEnded
    );
}


function scheduleIdleTalk() {
    if (
        idleTalkTimerId !== null ||
        !canRunAutomaticBroadcast() ||
        !isEventQueueIdle()
    ) {
        return;
    }

    idleTalkTimerId = setTimeout(() => {
        idleTalkTimerId = null;

        if (
            !canRunAutomaticBroadcast() ||
            !isEventQueueIdle()
        ) {
            return;
        }

        enqueueIdleTalk();
    }, IDLE_TALK_DELAY_MS);
}


function cancelIdleTalkTimer() {
    if (idleTalkTimerId === null) {
        return;
    }

    clearTimeout(idleTalkTimerId);
    idleTalkTimerId = null;
}


function enqueueIdleTalk() {
    const talkType = nextIdleTalkType;

    nextIdleTalkType =
        talkType === "news"
            ? "weather"
            : "news";

    enqueueEvent(
        `${talkType}_talk`,
        EVENT_PRIORITY.IDLE_TALK,
        () => runIdleTalk(talkType)
    );

    writeSystemLog(
        ui,
        `${
            talkType === "news"
                ? "ニューストーク"
                : "ウェザートーク"
        }をキューへ追加しました`
    );
}


async function runIdleTalk(talkType) {
    const label =
        talkType === "news"
            ? "ニューストーク"
            : "ウェザートーク";

    showIdleTalkProcessing(
        ui,
        talkType
    );

    writeSystemLog(
        ui,
        `${label}を開始しました`
    );

    try {
        if (talkType === "news") {
            await generateNewsTalk(ui);
        } else {
            await generateWeatherTalk(ui);
        }

        showIdleTalkCompleted(ui);

        writeSystemLog(
            ui,
            `${label}を終了しました`
        );

    } catch (error) {
        console.error(
            `${label}処理エラー:`,
            error
        );

        showIdleTalkError(
            ui,
            talkType
        );

        writeSystemLog(
            ui,
            `${label}エラー: ${
                error?.message || "不明なエラー"
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
    liveState.broadcastStarted = false;

    cancelIdleTalkTimer();
    clearEventQueue();
    showLiveStopped(ui);

    writeSystemLog(
        ui,
        "コメント取得と自動処理を停止しました"
    );
}


export function destroyLivePage() {
    stopYouTubeLiveCommentPolling();

    liveState.broadcastStarted = false;

    cancelIdleTalkTimer();
    clearEventQueue();
}
