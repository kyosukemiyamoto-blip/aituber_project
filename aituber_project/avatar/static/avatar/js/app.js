import { VTubeStudioManager } from "./vtube_studio.js";

document.addEventListener("DOMContentLoaded", () => {
    // ==============================
    // DOM
    // ==============================
    const commentList = document.getElementById("commentList");
    const eventQueue = document.getElementById("eventQueue");

    const vtubeHost = document.getElementById("vtubeHost");
    const connectVTubeBtn = document.getElementById("connectVTubeBtn");
    const vtubeStatusText = document.getElementById("vtubeStatusText");
    const currentExpression = document.getElementById("currentExpression");

    const generateSuperChatBtn = document.getElementById("generateSuperChatBtn");
    const generateCommentBtn = document.getElementById("generateCommentBtn");
    const generateSelfIntroductionBtn = document.getElementById("generateSelfIntroductionBtn");
    const generateNewsTalkBtn = document.getElementById("generateNewsTalkBtn");
    const generateWeatherTalkBtn = document.getElementById("generateWeatherTalkBtn");
    const sendUserCommentBtn = document.getElementById("sendUserCommentBtn");

    // ==============================
    // Queue state
    // ==============================
    const eventQueueData = [];
    let isProcessing = false;

    // ==============================
    // VTube Studio state
    // ==============================
    let vtubeManager = null;
    let vtubeConnected = false;

    // ==============================
    // VTube Studio connection
    // ==============================
    async function connectVTubeStudio() {
        const url = vtubeHost.value.trim() || "ws://localhost:8001";

        try {
            connectVTubeBtn.disabled = true;
            connectVTubeBtn.textContent = "接続中...";
            vtubeStatusText.textContent = "接続中...";

            vtubeManager = new VTubeStudioManager(url);
            await vtubeManager.initialize();

            vtubeConnected = true;
            window.vtubeManager = vtubeManager;

            connectVTubeBtn.textContent = "接続済み";
            vtubeStatusText.textContent = "接続済み";

            console.log("VTube Studio connected");

        } catch (error) {
            console.error("VTube Studio connection error:", error);

            vtubeConnected = false;
            vtubeManager = null;

            connectVTubeBtn.disabled = false;
            connectVTubeBtn.textContent = "再接続";
            vtubeStatusText.textContent = "接続失敗";

            alert(
                "VTube Studio接続に失敗しました。\n\n" +
                "確認事項:\n" +
                "1. VTube Studioが起動しているか\n" +
                "2. VTube StudioのPlugin APIが有効か\n" +
                "3. URLが ws://localhost:8001 になっているか"
            );
        }
    }

    async function applyVTubeStudioExpression(emotion) {
        if (!vtubeConnected || !vtubeManager || !vtubeManager.isConnected()) {
            console.warn("VTube Studio未接続のため表情変更をスキップ");
            return;
        }

        const normalizedEmotion = (emotion || "normal").toUpperCase();

        try {
            await vtubeManager.changeExpression(normalizedEmotion);

            if (currentExpression) {
                currentExpression.textContent = normalizedEmotion;
            }

        } catch (error) {
            console.error("VTube Studio expression error:", error);
        }
    }

    async function runVTubeStudioLipSync(lipSyncData = [], voiceSpeed = 1.0) {
        if (!vtubeConnected || !vtubeManager || !vtubeManager.isConnected()) {
            console.warn("VTube Studio未接続のためリップシンクをスキップ");
            return;
        }

        if (!Array.isArray(lipSyncData) || lipSyncData.length === 0) {
            console.warn("lip_sync が空のためリップシンクをスキップ");
            return;
        }

        try {
            await vtubeManager.lipSync(lipSyncData, voiceSpeed);
        } catch (error) {
            console.error("VTube Studio lipSync error:", error);
        }
    }

    connectVTubeBtn.addEventListener("click", connectVTubeStudio);

    // ==============================
    // Comment UI
    // ==============================
    function escapeHTML(value) {
        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function addCommentToUI(comment, type = "normal") {
        const item = document.createElement("div");
        item.className = `comment_item ${type}`;

        const username = comment.username || "unknown";
        const text = comment.text || "";
        const time = comment.time || "now";

        item.innerHTML = `
            <div class="avatar">${escapeHTML(username.charAt(0).toUpperCase())}</div>
            <div class="comment_body">
                <div class="comment_meta">
                    <span class="username">${escapeHTML(username)}</span>
                    <span class="time">${escapeHTML(time)}</span>
                </div>
                <p>${escapeHTML(text)}</p>
            </div>
        `;

        commentList.appendChild(item);
        commentList.scrollTop = commentList.scrollHeight;
    }

    // ==============================
    // Reply payload
    // ==============================
    function extractReplyPayload(data) {
        const reply = data.reply || data;

        return {
            script: reply.script || "",
            emotion: reply.emotion || "normal",
            audioId: reply.audio_id || data.audio_id || null,
            audioUrl: reply.audio_url || data.audio_url || null,
            lipSync: reply.lip_sync || data.lip_sync || []
        };
    }

    async function deleteVoiceFile(audioId) {
        if (!audioId) return;

        try {
            const response = await fetch("/api/delete-voice/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    audio_id: audioId
                })
            });

            const result = await response.json();
            console.log("voice delete result:", result);

        } catch (error) {
            console.error("voice delete error:", error);
        }
    }

    async function playVoiceWithLipSyncAndCleanup(reply) {
        const { audioId, audioUrl, lipSync } = reply;

        if (!audioUrl) {
            console.warn("audio_url がないため音声再生をスキップ");
            return;
        }

        const audio = new Audio(audioUrl);

        audio.addEventListener("play", () => {
            runVTubeStudioLipSync(lipSync, 1.0);
        });

        audio.addEventListener("ended", async () => {
            await deleteVoiceFile(audioId);
        });

        audio.addEventListener("error", async (error) => {
            console.error("audio playback error:", error);
            await deleteVoiceFile(audioId);
        });

        try {
            await audio.play();
        } catch (error) {
            console.error("audio play failed:", error);
            await deleteVoiceFile(audioId);
        }
    }

    async function handleAvatarResult(data) {
        const reply = extractReplyPayload(data);

        console.log("script:", reply.script);
        console.log("emotion:", reply.emotion);
        console.log("audioId:", reply.audioId);
        console.log("audioUrl:", reply.audioUrl);
        console.log("lipSync:", reply.lipSync);

        // 表情変更は音声再生前に実行
        await applyVTubeStudioExpression(reply.emotion);

        // 音声再生開始と同時に lip_sync 開始
        await playVoiceWithLipSyncAndCleanup(reply);
    }

    // ==============================
    // Queue
    // ==============================
    function addEventToQueue(type, priority) {
        const item = document.createElement("div");
        item.textContent = `[${priority}] ${type}`;

        eventQueue.appendChild(item);
        eventQueue.scrollTop = eventQueue.scrollHeight;
    }

    function enqueueEvent(type, priority, handler) {
        const event = {
            type,
            priority,
            handler
        };

        eventQueueData.push(event);
        eventQueueData.sort((a, b) => b.priority - a.priority);

        renderEventQueue();
        processQueue();
    }

    function renderEventQueue() {
        eventQueue.innerHTML = "";

        eventQueueData.forEach(event => {
            const item = document.createElement("div");
            item.textContent = `[${event.priority}] ${event.type}`;
            eventQueue.appendChild(item);
        });
    }

    async function processQueue() {
        if (isProcessing) return;

        isProcessing = true;

        while (eventQueueData.length > 0) {
            const event = eventQueueData.shift();
            renderEventQueue();

            try {
                await event.handler();
            } catch (error) {
                console.error("queue handler error:", error);
            }
        }

        isProcessing = false;
    }

    // ==============================
    // API handlers
    // ==============================
    async function generateSuperChat() {
        try {
            addEventToQueue("generate_superchat", 100);

            const response = await fetch("/api/generate-comment/");
            const data = await response.json();

            addCommentToUI(data.comment, "superchat");

            const replyResponse = await fetch("/api/reply-to-comment/");
            const replyData = await replyResponse.json();

            await handleAvatarResult(replyData);

        } catch (error) {
            console.error("スーパーチャット生成/返信エラー:", error);
        }
    }

    async function generateCommentAutomatically() {
        try {
            addEventToQueue("generate_comment", 2);

            const response = await fetch("/api/generate-comment/");
            const data = await response.json();

            addCommentToUI(data.comment);

            const replyResponse = await fetch("/api/reply-to-comment/");
            const replyData = await replyResponse.json();

            await handleAvatarResult(replyData);

        } catch (error) {
            console.error("コメント生成/返信エラー:", error);
        }
    }

    async function generateSelfIntroduction() {
        try {
            addEventToQueue("generate_self_introduction", 1);

            const response = await fetch("/api/self-introduction/");
            const data = await response.json();

            await handleAvatarResult(data);

        } catch (error) {
            console.error("自己紹介生成エラー:", error);
        }
    }

    async function generateNewsTalk() {
        try {
            addEventToQueue("generate_news_talk", 1);

            const response = await fetch("/api/news-talk/");
            const data = await response.json();

            await handleAvatarResult(data);

        } catch (error) {
            console.error("ニューストーク生成エラー:", error);
        }
    }

    async function generateWeatherTalk() {
        try {
            addEventToQueue("generate_weather_talk", 1);

            const response = await fetch("/api/weather-talk/");
            const data = await response.json();

            await handleAvatarResult(data);

        } catch (error) {
            console.error("ウェザートーク生成エラー:", error);
        }
    }

    async function sendUserComment() {
        const usernameInput = document.getElementById("usernameInput");
        const messageInput = document.getElementById("messageInput");

        const username = usernameInput.value.trim();
        const message = messageInput.value.trim();

        if (!username || !message) return;

        try {
            addCommentToUI({
                username: username,
                text: message,
                time: "now"
            });

            messageInput.value = "";

            const response = await fetch("/api/user-comment/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username,
                    message
                })
            });

            const data = await response.json();

            console.log("user comment response:", data);

            await handleAvatarResult(data);

        } catch (error) {
            console.error("user comment error:", error);
        }
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

    sendUserCommentBtn.addEventListener("click", sendUserComment);

    document.getElementById("messageInput").addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            sendUserComment();
        }
    });
});