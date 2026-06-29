import {
    initializeVTubeStudioBridge
} from "./aituber_vtube_bridge.js";

import {
    initializeEventQueue,
    enqueueEvent
} from "./event_queue.js";


import {
    initializeCommentUI
} from "./comment_ui.js";


import {
    generateSuperChat,
    generateCommentAutomatically,
    generateSelfIntroduction,
    generateNewsTalk,
    generateWeatherTalk,
    sendUserComment
} from "./avatar_actions.js";


document.addEventListener("DOMContentLoaded", () => {
    initializeVTubeStudioBridge();

    // ==============================
    // DOM
    // ==============================
    const commentList = document.getElementById("commentList");
    const eventQueue = document.getElementById("eventQueue");

    initializeCommentUI(commentList);
    initializeEventQueue(eventQueue);
    // ==============================
    // DOM
    // ==============================
    const generateSuperChatBtn = document.getElementById("generateSuperChatBtn");
    const generateCommentBtn = document.getElementById("generateCommentBtn");
    const generateSelfIntroductionBtn = document.getElementById("generateSelfIntroductionBtn");
    const generateNewsTalkBtn = document.getElementById("generateNewsTalkBtn");
    const generateWeatherTalkBtn = document.getElementById("generateWeatherTalkBtn");
    const sendUserCommentBtn = document.getElementById("sendUserCommentBtn");

    
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

    // ==============================
    // Button events
    // ==============================
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
});