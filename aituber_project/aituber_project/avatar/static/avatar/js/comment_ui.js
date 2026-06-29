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
export function addCommentToUI(comment, type = "normal") {
    if (!commentListElement) {
        console.warn("コメント表示先が初期化されていません");
        return;
    }

    const item = document.createElement("div");
    item.className = `comment_item ${type}`;

    const username = comment.username || "unknown";
    const text = comment.text || "";
    const time = comment.time || "now";

    item.innerHTML = `
        <div class="avatar">
            ${escapeHTML(username.charAt(0).toUpperCase())}
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
}