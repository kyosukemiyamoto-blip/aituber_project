import { VTubeStudioManager } from "./vtube_studio.js";


let vtubeManager = null;
let vtubeConnected = false;

let connectVTubeBtn = null;
let vtubeHost = null;
let vtubeStatusText = null;
let currentExpression = null;



export function initializeVTubeStudioBridge() {
    connectVTubeBtn = document.getElementById("connectVTubeBtn");
    vtubeHost = document.getElementById("vtubeHost");
    vtubeStatusText = document.getElementById("vtubeStatusText");
    currentExpression = document.getElementById("currentExpression");

    if (connectVTubeBtn) {
        connectVTubeBtn.addEventListener("click", () => {
            void connectVTubeStudio().catch(() => {});
        });
    }
}



export async function connectVTubeStudio(
    urlOverride = null,
    { showAlert = true } = {}
) {
    const url =
        urlOverride ||
        vtubeHost?.value.trim() ||
        "ws://localhost:8001";

    try {
        updateConnectionUI("connecting");

        if (vtubeManager) {
            vtubeManager.disconnect();
        }

        vtubeManager = new VTubeStudioManager(url);
        await vtubeManager.initialize();

        vtubeConnected = true;
        updateConnectionUI("connected");

        console.log("VTube Studio connected");
        return true;

    } catch (error) {
        console.error("VTube Studio接続エラー:", error);

        if (vtubeManager) {
            vtubeManager.disconnect();
        }

        vtubeConnected = false;
        vtubeManager = null;
        updateConnectionUI("failed");

        if (showAlert) {
            alert(
                "VTube Studio接続に失敗しました。\n\n" +
                "1. VTube Studioが起動しているか\n" +
                "2. Plugin APIが有効か\n" +
                "3. URLが ws://localhost:8001 か"
            );
        }

        throw error;
    }
}

export function isVTubeStudioConnected() {
    return canUseVTubeStudio();
}



function updateConnectionUI(status) {
    if (!connectVTubeBtn || !vtubeStatusText) {
        return;
    }

    switch (status) {
        case "connecting":
            connectVTubeBtn.disabled = true;
            connectVTubeBtn.textContent = "接続中...";
            vtubeStatusText.textContent = "接続中...";
            break;

        case "connected":
            connectVTubeBtn.disabled = true;
            connectVTubeBtn.textContent = "接続済み";
            vtubeStatusText.textContent = "接続済み";
            break;

        case "failed":
            connectVTubeBtn.disabled = false;
            connectVTubeBtn.textContent = "再接続";
            vtubeStatusText.textContent = "接続失敗";
            break;
    }
}



function canUseVTubeStudio() {
    return Boolean(
        vtubeConnected &&
        vtubeManager &&
        vtubeManager.isConnected()
    );
}



export async function applyVTubeStudioExpression(emotion) {
    if (!canUseVTubeStudio()) {
        console.warn("VTube Studio未接続のため表情変更をスキップ");
        return;
    }

    const normalizedEmotion = String(
        emotion || "normal"
    ).toUpperCase();

    try {
        await vtubeManager.changeExpression(normalizedEmotion);

        if (currentExpression) {
            currentExpression.textContent = normalizedEmotion;
        }

    } catch (error) {
        console.error("VTube Studio表情変更エラー:", error);
    }
}



export async function runVTubeStudioLipSync(
    lipSyncData = [],
    voiceSpeed = 1.0
) {
    if (!canUseVTubeStudio()) {
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
        console.error("VTube Studioリップシンクエラー:", error);
    }
}



export function disconnectVTubeStudio() {
    if (vtubeManager) {
        vtubeManager.disconnect();
    }

    vtubeManager = null;
    vtubeConnected = false;
}