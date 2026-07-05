let commentListElement = null;

export function initializeCommentUI(element) {
    commentListElement = element;

    if (!commentListElement) {
        console.warn("commentList が見つかりません");
    }
}


function escapeHTML(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/**
 * コメントをコメント欄へ追加する。
 */
const MAX_LIVE_COMMENTS = 10;

export function addCommentToUI(comment, type = "normal") {
    if (!commentListElement) {
        console.warn("コメント表示先が初期化されていません");
        return null;
    }

    const item = document.createElement("div");
    item.className = `comment_item ${type}`;

    const username = comment.username || "unknown";
    const text = comment.text || "";
    const time = comment.time || "now";

    // アバターでは先頭の@を除外
    const avatarName = username.replace(/^@+/, "");
    const avatarLetter =
        avatarName.charAt(0).toUpperCase() || "?";

    item.innerHTML = `
        <div class="avatar">
            ${escapeHTML(avatarLetter)}
        </div>

        <div class="comment_body">
            <div class="comment_meta">
                <span class="username">
                    ${escapeHTML(username)}
                </span>

                <span class="time">
                    ${escapeHTML(time)}
                </span>
            </div>

            <p>${escapeHTML(text)}</p>
        </div>
    `;

    commentListElement.appendChild(item);
    commentListElement.scrollTop =
        commentListElement.scrollHeight;

    return item;
}


export function addCommentsToUI(comments, type = "normal") {
    if (!Array.isArray(comments)) {
        console.warn("comments は配列で渡してください");
        return;
    }

    if (!commentListElement || comments.length === 0) {
        return;
    }

    const emptyMessage =
        commentListElement.querySelector(".empty_message");

    if (emptyMessage) {
        emptyMessage.remove();
    }

    for (const comment of comments) {
        const item = addCommentToUI(comment, type);

        if (item) {
            commentListElement.prepend(item);
        }
    }

    const commentItems =
        commentListElement.querySelectorAll(".comment_item");

    for (
        let index = MAX_LIVE_COMMENTS;
        index < commentItems.length;
        index++
    ) {
        commentItems[index].remove();
    }

    commentListElement.scrollTop = 0;
}