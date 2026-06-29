export async function fetchJSON(url, options = {}) {
    let response;

    try {
        response = await fetch(url, options);
    } catch (error) {
        throw new Error(
            "サーバーに接続できませんでした。",
            { cause: error }
        );
    }

    let data;

    try {
        data = await response.json();
    } catch (error) {
        throw new Error(
            `サーバーから不正なレスポンスが返されました。HTTP ${response.status}`,
            { cause: error }
        );
    }

    if (!response.ok) {
        const error = new Error(
            data.error ||
            `APIエラーが発生しました。HTTP ${response.status}`
        );

        error.status = response.status;
        error.code = data.code || "UNKNOWN_API_ERROR";
        error.data = data;

        throw error;
    }

    return data;
}