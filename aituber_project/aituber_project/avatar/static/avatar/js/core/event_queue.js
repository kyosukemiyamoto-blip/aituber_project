let eventQueueElement = null;

const eventQueueData = [];
let isProcessing = false;



export function initializeEventQueue(element) {
    eventQueueElement = element;
    renderEventQueue();
}



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