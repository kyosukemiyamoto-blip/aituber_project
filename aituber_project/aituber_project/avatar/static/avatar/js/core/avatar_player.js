import { fetchJSON } from "./api_client.js";

import {
    applyVTubeStudioExpression,
    runVTubeStudioLipSync
} from "./aituber_vtube_bridge.js";



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


export async function handleAvatarResult(data, ui = null) {
    const reply = extractReplyPayload(data);

    console.log("script:", reply.script);
    console.log("emotion:", reply.emotion);
    console.log("audioId:", reply.audioId);
    console.log("audioUrl:", reply.audioUrl);
    console.log("lipSync:", reply.lipSync);

    if (ui) {
        showCurrentReply(ui, reply);
    }

    await applyVTubeStudioExpression(
        reply.emotion
    );

    await playVoiceWithLipSyncAndCleanup(
        reply
    );

    return reply;
}

export function showCurrentReply(ui, reply) {
    ui.currentReplyText.textContent =
        reply.script || "返信内容がありません。";

    ui.currentReplyEmotion.textContent =
        reply.emotion || "-";

    ui.currentAudioStatus.textContent =
        reply.audioUrl ? "音声生成済み" : "音声なし";

    ui.replyProcessStatus.textContent =
        "再生中";
}