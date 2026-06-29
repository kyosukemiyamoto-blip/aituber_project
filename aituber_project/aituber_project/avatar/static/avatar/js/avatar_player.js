import { fetchJSON } from "./api_client.js";

import {
    applyVTubeStudioExpression,
    runVTubeStudioLipSync
} from "./aituber_vtube_bridge.js";


/**
 * APIレスポンスからアバター再生に必要な情報を取り出す。
 */
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


/**
 * 再生済み音声ファイルをサーバーから削除する。
 */
async function deleteVoiceFile(audioId) {
    if (!audioId) {
        return;
    }

    try {
        const result = await fetchJSON("/api/delete-voice/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                audio_id: audioId
            })
        });

        console.log("voice delete result:", result);

    } catch (error) {
        console.error("voice delete error:", error);
    }
}


/**
 * 音声を再生し、同時にリップシンクを開始する。
 * 再生終了後は音声ファイルを削除する。
 */
function playVoiceWithLipSyncAndCleanup(reply) {
    return new Promise((resolve, reject) => {
        const {
            audioId,
            audioUrl,
            lipSync
        } = reply;

        if (!audioUrl) {
            console.warn(
                "audio_url がないため音声再生をスキップ"
            );

            resolve();
            return;
        }

        const audio = new Audio(audioUrl);

        audio.addEventListener("play", () => {
            void runVTubeStudioLipSync(
                lipSync,
                1.0
            );
        });

        audio.addEventListener("ended", async () => {
            await deleteVoiceFile(audioId);
            resolve();
        });

        audio.addEventListener("error", async event => {
            console.error(
                "audio playback error:",
                event
            );

            await deleteVoiceFile(audioId);

            reject(
                new Error("音声の再生に失敗しました")
            );
        });

        audio.play().catch(async error => {
            console.error(
                "audio play failed:",
                error
            );

            await deleteVoiceFile(audioId);
            reject(error);
        });
    });
}


/**
 * APIレスポンスを受け取り、
 * 表情変更と音声・リップシンク再生を実行する。
 */
export async function handleAvatarResult(data) {
    const reply = extractReplyPayload(data);

    console.log("script:", reply.script);
    console.log("emotion:", reply.emotion);
    console.log("audioId:", reply.audioId);
    console.log("audioUrl:", reply.audioUrl);
    console.log("lipSync:", reply.lipSync);

    await applyVTubeStudioExpression(
        reply.emotion
    );

    await playVoiceWithLipSyncAndCleanup(
        reply
    );
}