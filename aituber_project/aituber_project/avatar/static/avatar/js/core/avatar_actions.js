import { fetchJSON } from "./api_client.js";
import { addCommentToUI } from "./comment_ui.js";
import { handleAvatarResult } from "./avatar_player.js";


export async function generateSuperChat() {
    try {
        const data = await fetchJSON(
            "/api/generate-comment/"
        );

        addCommentToUI(
            data.comment,
            "superchat"
        );

        const replyData = await fetchJSON(
            "/api/reply-to-comment/"
        );

        await handleAvatarResult(replyData);

    } catch (error) {
        console.error(
            "スーパーチャット生成/返信エラー:",
            error
        );
    }
}


export async function generateCommentAutomatically() {
    try {
        const data = await fetchJSON(
            "/api/generate-comment/"
        );

        addCommentToUI(data.comment);

        const replyData = await fetchJSON(
            "/api/reply-to-comment/"
        );

        await handleAvatarResult(replyData);

    } catch (error) {
        console.error(
            "コメント生成/返信エラー:",
            error
        );
    }
}


export async function generateSelfIntroduction(ui = null) {
    try {
        const data = await fetchJSON(
            "/api/self-introduction/"
        );

        return await handleAvatarResult(
            data,
            ui
        );

    } catch (error) {
        console.error(
            "自己紹介生成エラー:",
            error
        );

        if (ui) {
            ui.replyProcessStatus.textContent =
                "エラー";
        }

        throw error;
    }
}


export async function generateNewsTalk(ui = null) {
    try {
        const data = await fetchJSON(
            "/api/news-talk/"
        );

        return await handleAvatarResult(data, ui);

    } catch (error) {
        console.error(
            "ニューストーク生成エラー:",
            error
        );

        throw error;
    }
}


export async function generateWeatherTalk(ui = null) {
    try {
        const data = await fetchJSON(
            "/api/weather-talk/"
        );

        return await handleAvatarResult(data, ui);

    } catch (error) {
        console.error(
            "ウェザートーク生成エラー:",
            error
        );

        throw error;
    }
}


export async function replyToLiveComment(comment, ui = null) {
    const username = String(comment?.username || "viewer").trim();

    const message = String(comment?.text || "").trim();

    if (!message) {
        throw new Error("返信対象のコメント本文が空です");
    }

    try {
        const data = await fetchJSON(
            "/api/user-comment/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username,
                    message
                })
            }
        );

        return await handleAvatarResult(
            data,
            ui
        );

    } catch (error) {
        console.error(
            "YouTube Liveコメント返信エラー:",
            error
        );

        throw error;
    }
}


export async function sendUserComment(
    username,
    message
) {
    addCommentToUI({
        username,
        text: message,
        time: "now"
    });

    return await replyToLiveComment({
        username,
        text: message,
        time: "now"
    });
}

export async function useScriptDirectly(script, emotion) {
    if (!script || !emotion) {
        throw new Error("scriptとemotionがセットされていません");
    }

    try {
        const data = await fetchJSON("/api/use-script-directly/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                script,
                emotion
            })
        });

        return await handleAvatarResult(data);

    } catch (error) {
        console.error("ManualScript作成エラー:", error);
        throw error;
    }
}

export async function scriptWithInstruction(instruction){
    if(!instruction){
        throw new Error("instructionがセットされていません");
    }

    try{
        const data = await fetchJSON("/api/script-with-instruction/",{
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                instruction
            })
        });

        return await handleAvatarResult(data);

    } catch (error){
        console.error("scriptWithInstructionエラー", error);
        throw error;
    }
}