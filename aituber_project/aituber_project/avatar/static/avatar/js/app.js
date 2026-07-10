import {
    initializeVTubeStudioBridge
} from "./core/aituber_vtube_bridge.js";

import {
    initializeEventQueue,
    enqueueEvent
} from "./core/event_queue.js";


import {
    initializeCommentUI
} from "./core/comment_ui.js";


import {
    generateSuperChat,
    generateCommentAutomatically,
    generateSelfIntroduction,
    generateNewsTalk,
    generateWeatherTalk,
    sendUserComment
} from "./core/avatar_actions.js";

import {
    getYouTubeLiveInfo
} from "./live/youtube_live_api.js";

document.addEventListener("DOMContentLoaded", () => {
    initializeVTubeStudioBridge();


    const commentList = document.getElementById("commentList");
    const eventQueue = document.getElementById("eventQueue");

    initializeCommentUI(commentList);
    initializeEventQueue(eventQueue);

    const generateSuperChatBtn = document.getElementById("generateSuperChatBtn");
    const generateCommentBtn = document.getElementById("generateCommentBtn");
    const generateSelfIntroductionBtn = document.getElementById("generateSelfIntroductionBtn");
    const generateNewsTalkBtn = document.getElementById("generateNewsTalkBtn");
    const generateWeatherTalkBtn = document.getElementById("generateWeatherTalkBtn");
    const sendUserCommentBtn = document.getElementById("sendUserCommentBtn");


    const liveUrlInput = document.getElementById("liveUrlInput");
    const connectLiveBtn = document.getElementById("connectLiveBtn");
    const liveConnectionStatus = document.getElementById("liveConnectionStatus");


    function enqueueUserComment() {
        const usernameInput =
            document.getElementById("usernameInput");

        const messageInput =
            document.getElementById("messageInput");

        const username = usernameInput.value.trim();
        const message = messageInput.value.trim();

        if (!username || !message) {
            return;
        }

        messageInput.value = "";

        enqueueEvent(
            "user_comment",
            50,
            () => sendUserComment(username, message)
        );
    }


    generateSuperChatBtn.addEventListener("click", () => {
        enqueueEvent("generate_superchat", 100, generateSuperChat);
    });

    generateCommentBtn.addEventListener("click", () => {
        enqueueEvent("generate_comment", 2, generateCommentAutomatically);
    });

    generateSelfIntroductionBtn.addEventListener("click", () => {
        enqueueEvent("generate_self_introduction", 1, generateSelfIntroduction);
    });

    generateNewsTalkBtn.addEventListener("click", () => {
        enqueueEvent("generate_news_talk", 1, generateNewsTalk);
    });

    generateWeatherTalkBtn.addEventListener("click", () => {
        enqueueEvent("generate_weather_talk", 1, generateWeatherTalk);
    });

    sendUserCommentBtn.addEventListener(
        "click",
        enqueueUserComment
    );

    document.getElementById("messageInput").addEventListener(
        "keydown",
        event => {
            if (event.key === "Enter") {
                enqueueUserComment();
            }
        }
    );

    connectLiveBtn.addEventListener("click", async () => {
        const liveUrl = liveUrlInput.value.trim();

        if (!liveUrl) {
            liveConnectionStatus.textContent =
                "YouTube Live URLを入力してください";

            return;
        }

        connectLiveBtn.disabled = true;
        liveConnectionStatus.textContent =
            "配信情報を取得中...";

        try {
            const liveInfo =
                await getYouTubeLiveInfo(liveUrl);

            if (!liveInfo.liveChatId) {
                throw new Error(
                    "Live Chat IDを取得できませんでした"
                );
            }

            const liveSetupData = {
                liveUrl,
                title: liveInfo.title || "",
                videoId: liveInfo.videoId || "",
                liveChatId: liveInfo.liveChatId
            };

            sessionStorage.setItem(
                "aituberLiveSetup",
                JSON.stringify(liveSetupData)
            );

            liveConnectionStatus.textContent =
                "接続確認完了";

            const livePageUrl =
                connectLiveBtn.dataset.livePageUrl;

            window.location.assign(livePageUrl);

        } catch (error) {
            console.error(
                "YouTube Live接続エラー:",
                error
            );

            liveConnectionStatus.textContent =
                error.message ||
                "配信への接続に失敗しました";

            connectLiveBtn.disabled = false;
        }
    });
});