let eventQueueElement = null;

const eventQueueData = [];
let isProcessing = false;


/**
 * キュー表示用のDOMを設定する。
 */
export function initializeEventQueue(element) {
    eventQueueElement = element;
    renderEventQueue();
}


/**
 * イベントをキューへ追加する。
 */
export function enqueueEvent(type, priority, handler) {
    if (typeof handler !== "function") {
        throw new TypeError("handler must be a function");
    }

    const event = {
        type,
        priority,
        handler
    };

    eventQueueData.push(event);

    eventQueueData.sort((a, b) => {
        return b.priority - a.priority;
    });

    renderEventQueue();

    void processQueue();
}


/**
 * 現在のキューを画面へ表示する。
 */
function renderEventQueue() {
    if (!eventQueueElement) {
        return;
    }

    eventQueueElement.innerHTML = "";

    eventQueueData.forEach(event => {
        const item = document.createElement("div");

        item.textContent = `[${event.priority}] ${event.type}`;

        eventQueueElement.appendChild(item);
    });

    eventQueueElement.scrollTop =
        eventQueueElement.scrollHeight;
}


/**
 * キューを先頭から順番に実行する。
 */
async function processQueue() {
    if (isProcessing) {
        return;
    }

    isProcessing = true;

    try {
        while (eventQueueData.length > 0) {
            const event = eventQueueData.shift();

            renderEventQueue();

            try {
                await event.handler();
            } catch (error) {
                console.error(
                    `queue handler error: ${event.type}`,
                    error
                );
            }
        }
    } finally {
        isProcessing = false;
    }
}