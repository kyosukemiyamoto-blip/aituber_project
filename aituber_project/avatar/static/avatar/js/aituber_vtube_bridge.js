// avatar/static/avatar/js/aituber_vtube_bridge.js

import { VTubeStudioManager } from "./vtube_studio.js";

let vtubeManager = null;
let vtubeConnected = false;

const connectVTubeBtn = document.getElementById("connectVTubeBtn");
const vtubeHost = document.getElementById("vtubeHost");
const vtubeStatusText = document.getElementById("vtubeStatusText");
const currentExpression = document.getElementById("currentExpression");

connectVTubeBtn.addEventListener("click", async () => {
    const url = vtubeHost.value.trim() || "ws://localhost:8001";

    try {
        connectVTubeBtn.disabled = true;
        connectVTubeBtn.textContent = "接続中...";
        vtubeStatusText.textContent = "接続中...";

        vtubeManager = new VTubeStudioManager(url);
        await vtubeManager.initialize();

        vtubeConnected = true;
        window.vtubeManager = vtubeManager;

        vtubeStatusText.textContent = "接続済み";
        connectVTubeBtn.textContent = "接続済み";

        console.log("VTube Studio connected");

    } catch (error) {
        console.error("VTube Studio接続エラー:", error);

        vtubeConnected = false;
        vtubeStatusText.textContent = "接続失敗";
        connectVTubeBtn.textContent = "再接続";
        connectVTubeBtn.disabled = false;

        alert(
            "VTube Studio接続に失敗しました。\n\n" +
            "確認事項:\n" +
            "1. VTube Studioが起動しているか\n" +
            "2. Plugin APIが有効か\n" +
            "3. URLが ws://localhost:8001 になっているか"
        );
    }
});

export async function applyVTubeStudioMotion(emotion, lipSyncData, voiceSpeed = 1.0) {
    if (!vtubeConnected || !vtubeManager || !vtubeManager.isConnected()) {
        console.warn("VTube Studio未接続のためスキップ");
        return;
    }

    const normalizedEmotion = (emotion || "normal").toUpperCase();

    await vtubeManager.changeExpression(normalizedEmotion);

    if (currentExpression) {
        currentExpression.textContent = normalizedEmotion;
    }

    if (Array.isArray(lipSyncData) && lipSyncData.length > 0) {
        await vtubeManager.lipSync(lipSyncData, voiceSpeed);
    }
}