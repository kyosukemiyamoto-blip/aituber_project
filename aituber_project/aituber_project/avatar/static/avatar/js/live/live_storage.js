const LIVE_SETUP_STORAGE_KEY = "aituberLiveSetup";


export function loadLiveSetupData() {
    const rawData = sessionStorage.getItem(
        LIVE_SETUP_STORAGE_KEY
    );

    if (!rawData) {
        return null;
    }

    try {
        const data = JSON.parse(rawData);

        if (
            !data ||
            typeof data !== "object" ||
            !data.liveChatId
        ) {
            console.error(
                "Live接続情報にliveChatIdがありません:",
                data
            );

            return null;
        }

        return {
            liveUrl: String(data.liveUrl || ""),
            title: String(data.title || ""),
            videoId: String(data.videoId || ""),
            liveChatId: String(data.liveChatId)
        };

    } catch (error) {
        console.error(
            "Live接続情報の解析エラー:",
            error
        );

        return null;
    }
}
