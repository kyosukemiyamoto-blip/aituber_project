function getRequiredElement(id) {
    const element = document.getElementById(id);

    if (!element) {
        throw new Error(`必須DOMが見つかりません: #${id}`);
    }

    return element;
}


export function getLiveElements() {
    return {
        liveStatusBadge:
            getRequiredElement("liveStatusBadge"),

        startBroadcastBtn:
            getRequiredElement("startBroadcastBtn"),

        stopLiveBtn:
            getRequiredElement("stopLiveBtn"),

        liveTitleText:
            getRequiredElement("liveTitleText"),

        videoIdText:
            getRequiredElement("videoIdText"),

        commentPollingStatus:
            getRequiredElement("commentPollingStatus"),

        currentCommentUsername:
            getRequiredElement("currentCommentUsername"),

        currentCommentTime:
            getRequiredElement("currentCommentTime"),

        currentCommentText:
            getRequiredElement("currentCommentText"),

        replyProcessStatus:
            getRequiredElement("replyProcessStatus"),

        currentReplyText:
            getRequiredElement("currentReplyText"),

        currentReplyEmotion:
            getRequiredElement("currentReplyEmotion"),

        currentAudioStatus:
            getRequiredElement("currentAudioStatus"),

        queueCount:
            getRequiredElement("queueCount"),

        eventQueue:
            getRequiredElement("eventQueue"),

        commentList:
            getRequiredElement("liveCommentList"),

        clearCommentsBtn:
            getRequiredElement("clearCommentsBtn"),

        systemLog:
            getRequiredElement("systemLog"),

        clearLogBtn:
            getRequiredElement("clearLogBtn"),

        manualScript:
            getRequiredElement("manualScriptInput"),

        manualEmotion:
            getRequiredElement("manualEmotionSelect"),

        speakManualScriptBtn:
            getRequiredElement("speakManualScriptBtn"),
    };
}
