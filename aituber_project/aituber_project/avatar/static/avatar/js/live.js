import {
    initializeLivePage,
    destroyLivePage
} from "./live/live_controller.js";


document.addEventListener("DOMContentLoaded", () => {
    try {
        initializeLivePage();
    } catch (error) {
        console.error("Liveページ初期化エラー:", error);
    }
});


window.addEventListener("beforeunload", () => {
    destroyLivePage();
});
