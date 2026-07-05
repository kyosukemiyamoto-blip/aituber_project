let activeLiveChatId = null;
let nextPageToken = null;
let pollingTimerId = null;
let abortController = null;
let isPolling = false;

export async function getCommentsFromYouTubeLiveChat(liveChatId, pageToken = null, signal = null) {
    if (!liveChatId) {
        throw new Error("liveChatIdが指定されていません");
    }

    const params = new URLSearchParams({ live_chat_id: liveChatId });

    if (pageToken) {
        params.set("page_token", pageToken);
    }

    const response = await fetch(`/api/youtube-live-comments/?${params}`, { signal });

    let data;

    try {
        data = await response.json();
    } catch {
        throw new Error("サーバーから不正なレスポンスが返されました");
    }

    if (!response.ok) {
        const message =
            data.error?.message ||
            data.error ||
            "コメント取得に失敗しました";

        throw new Error(message);
    }

    return {
        comments: Array.isArray(data.comments) ? data.comments : [],
        nextPageToken: data.nextPageToken || null,
        pollingIntervalMillis: Number(data.pollingIntervalMillis) || 5000,
        offlineAt: data.offlineAt || null,
    };
}

export function startYouTubeLiveCommentPolling({
    liveChatId,
    onComments,
    onStatus,
    onError,
    onLiveEnd,
}) {
    if (!liveChatId) {
        throw new Error("liveChatIdが指定されていません");
    }

    stopYouTubeLiveCommentPolling();

    activeLiveChatId = liveChatId;
    nextPageToken = null;
    isPolling = true;

    onStatus?.({
        status: "started",
        message: "コメント取得開始",
    });

    pollLiveComments({
        onComments,
        onStatus,
        onError,
        onLiveEnd,
    });
}

export function stopYouTubeLiveCommentPolling() {
    isPolling = false;
    activeLiveChatId = null;
    nextPageToken = null;

    if (pollingTimerId !== null) {
        clearTimeout(pollingTimerId);
        pollingTimerId = null;
    }

    if (abortController) {
        abortController.abort();
        abortController = null;
    }
}

export function isYouTubeLiveCommentPolling() {
    return isPolling;
}

async function pollLiveComments(callbacks) {
    if (!isPolling || !activeLiveChatId) {
        return;
    }

    const {
        onComments,
        onStatus,
        onError,
        onLiveEnd,
    } = callbacks;

    abortController = new AbortController();

    try {
        const data = await getCommentsFromYouTubeLiveChat(
            activeLiveChatId,
            nextPageToken,
            abortController.signal,
        );

        if (!isPolling) {
            return;
        }

        nextPageToken = data.nextPageToken || nextPageToken;

        if (data.comments.length > 0) {
            onComments?.(data.comments);
        }

        onStatus?.({
            status: "polling",
            message: `取得中（新着 ${data.comments.length}件）`,
            commentCount: data.comments.length,
        });

        if (data.offlineAt) {
            stopYouTubeLiveCommentPolling();

            onLiveEnd?.({
                offlineAt: data.offlineAt,
            });

            return;
        }

        scheduleNextPolling(data.pollingIntervalMillis, callbacks);
    } catch (error) {
        if (error.name === "AbortError") {
            return;
        }

        console.error("YouTube Liveコメント取得エラー:", error);

        onStatus?.({
            status: "error",
            message: "コメント取得エラー",
        });

        onError?.(error);

        if (isPolling) {
            scheduleNextPolling(5000, callbacks);
        }
    } finally {
        abortController = null;
    }
}

function scheduleNextPolling(intervalMillis, callbacks) {
    if (!isPolling) {
        return;
    }

    const safeInterval = Math.max(
        Number(intervalMillis) || 5000,
        1000,
    );

    pollingTimerId = setTimeout(() => {
        pollLiveComments(callbacks);
    }, safeInterval);
}


export async function getYouTubeLiveInfo(liveUrl) {
    const params = new URLSearchParams({
        live_url: liveUrl,
    });

    const response = await fetch(
        `/api/youtube-live-info/?${params}`
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.error ||
            "ライブ情報の取得に失敗しました"
        );
    }

    return data;
}