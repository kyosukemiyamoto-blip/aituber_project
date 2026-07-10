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


export async function generateNewsTalk() {
    try {
        const data = await fetchJSON(
            "/api/news-talk/"
        );

        await handleAvatarResult(data);

    } catch (error) {
        console.error(
            "ニューストーク生成エラー:",
            error
        );
    }
}


export async function generateWeatherTalk() {
    try {
        const data = await fetchJSON(
            "/api/weather-talk/"
        );

        await handleAvatarResult(data);

    } catch (error) {
        console.error(
            "ウェザートーク生成エラー:",
            error
        );
    }
}


export async function sendUserComment(
    username,
    message
) {
    try {
        addCommentToUI({
            username,
            text: message,
            time: "now"
        });

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

        console.log(
            "user comment response:",
            data
        );

        await handleAvatarResult(data);

    } catch (error) {
        console.error(
            "user comment error:",
            error
        );
    }
}