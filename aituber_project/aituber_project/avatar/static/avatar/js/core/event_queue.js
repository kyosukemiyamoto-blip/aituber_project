let eventQueueElement = null;

const eventQueueData = [];
let isProcessing = false;
let nextSequence = 0;
let onQueueChange = null;
let onQueueIdle = null;


export function initializeEventQueue(element,{onChange = null, onIdle = null} = {}) {
    eventQueueElement = element;
    onQueueChange = onChange;
    onQueueIdle = onIdle;

    eventQueueData.length = 0;
    isProcessing = false;
    nextSequence = 0;

    renderEventQueue();
    notifyQueueChange();
}


export function enqueueEvent(type, priority, handler) {
    if (typeof handler !== "function") {
        throw new TypeError("handler must be a function");
    }

    const event = {
        type,
        priority,
        handler,
        sequence: nextSequence++
    };

    eventQueueData.push(event);

    eventQueueData.sort((a, b) => {
        const priorityDifference =
            b.priority - a.priority;

        if (priorityDifference !== 0) {
            return priorityDifference;
        }

        return a.sequence - b.sequence;
    });

    renderEventQueue();
    notifyQueueChange();

    void processQueue();
}


export function clearEventQueue() {
    eventQueueData.length = 0;

    renderEventQueue();
    notifyQueueChange();
}


export function getEventQueueSize() {
    return eventQueueData.length;
}


export function isEventQueueIdle() {
    return (
        !isProcessing &&
        eventQueueData.length === 0
    );
}


function renderEventQueue() {
    if (!eventQueueElement) {
        return;
    }

    eventQueueElement.innerHTML = "";

    if (eventQueueData.length === 0) {
        const emptyMessage =
            document.createElement("p");

        emptyMessage.className = "empty_message";
        emptyMessage.textContent =
            isProcessing
                ? "イベントを処理中です。"
                : "待機中のイベントはありません。";

        eventQueueElement.appendChild(emptyMessage);
        return;
    }

    eventQueueData.forEach(event => {
        const item = document.createElement("div");

        item.textContent =
            `[${event.priority}] ${event.type}`;

        eventQueueElement.appendChild(item);
    });

    eventQueueElement.scrollTop =
        eventQueueElement.scrollHeight;
}


function notifyQueueChange() {
    if (typeof onQueueChange !== "function") {
        return;
    }

    onQueueChange({
        pendingCount: eventQueueData.length,
        isProcessing,
        isIdle: isEventQueueIdle()
    });
}


function notifyQueueIdle() {
    if (typeof onQueueIdle !== "function") {
        return;
    }

    try {
        void Promise.resolve(
            onQueueIdle()
        ).catch(error => {
            console.error(
                "queue idle handler error:",
                error
            );
        });
    } catch (error) {
        console.error(
            "queue idle handler error:",
            error
        );
    }
}


async function processQueue() {
    if (isProcessing) {
        return;
    }

    isProcessing = true;
    renderEventQueue();
    notifyQueueChange();

    try {
        while (eventQueueData.length > 0) {
            const event = eventQueueData.shift();

            renderEventQueue();
            notifyQueueChange();

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

        renderEventQueue();
        notifyQueueChange();

        if (eventQueueData.length === 0) {
            notifyQueueIdle();
        }
    }
}
