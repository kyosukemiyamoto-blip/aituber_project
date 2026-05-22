document.addEventListener("DOMContentLoaded", () => {
    const commentList = document.getElementById("commentList");
    const catAvatar = document.getElementById("catAvatar");
    const emotionImages = {
        normal: "/static/avatar/images/normal.png?v2",
        happy: "/static/avatar/images/happy.png?v2",
        surprised: "/static/avatar/images/surprised.png?v2",
        angry: "/static/avatar/images/angry.png?v2",
        sad: "/static/avatar/images/sad.png?v2"
    };

    const blinkFrames = [
        "/static/avatar/images/normal.png?v2",
        "/static/avatar/images/normal_2.png?v2",
        "/static/avatar/images/normal_3.png?v2",
        "/static/avatar/images/normal_2.png?v2",
        "/static/avatar/images/normal.png?v2"
    ];

    let isEmotionPlaying = false;

    const eventQueueData = [];
    let isProcessing = false;




    function addCommentToUI(comment, type="normal") {
        const item = document.createElement("div");
        item.className = `comment_item ${type}`;

        item.innerHTML = `
            <div class="avatar">${comment.username.charAt(0).toUpperCase()}</div>
            <div class="comment_body">
                <div class="comment_meta">
                    <span class="username">${comment.username}</span>
                    <span class="time">${comment.time}</span>
                </div>
                <p>${comment.text}</p>
            </div>
        `;

        commentList.appendChild(item);
        commentList.scrollTop = commentList.scrollHeight;
    }

function changeCatImage(emotion) {
    isEmotionPlaying = true;

    const imagePath = emotionImages[emotion] || emotionImages.normal;
    catAvatar.src = imagePath;
    setTimeout(() => {
        isEmotionPlaying = false; 
        catAvatar.src = blinkFrames[0];}, 3000);
}
function playBlinkAnimation() {
    if (isEmotionPlaying) return;
    let frameIndex = 0;
    const frameTimer = setInterval(() => {
        catAvatar.src = blinkFrames[frameIndex];
        frameIndex++;
        if (frameIndex >= blinkFrames.length) {
            clearInterval(frameTimer);
        }
    }, 80);
}

function startBlinkLoop() {

    setInterval(() => {
        const shouldBlink =
            Math.random() < 0.3;
        if (shouldBlink) {
            playBlinkAnimation();
        }
    }, 2000);
}


    async function generateSuperChat() {
        try {
            addEventToQueue("generate_superchat", 100);
            const response = await fetch("/api/generate-comment/");
            const data = await response.json();

            addCommentToUI(data.comment,"superchat");

            const replyResponse = await fetch("/api/reply-to-comment/");
            const replyData = await replyResponse.json();

            const reply = replyData.reply;
            const script = reply.script;
            const emotion = reply.emotion;

            console.log("script:", script);
            console.log("emotion:", emotion);

            changeCatImage(emotion);

        } catch (error) {
            console.error("コメント生成/返信エラー:", error);
        }
    }


    async function generateCommentAutomatically() {
        try {

            addEventToQueue("generate_comment",2);
            const response = await fetch("/api/generate-comment/");
            const data = await response.json();

            addCommentToUI(data.comment);

            const replyResponse = await fetch("/api/reply-to-comment/");
            const replyData = await replyResponse.json();

            const reply = replyData.reply;
            const script = reply.script;
            const emotion = reply.emotion;

            console.log("script:", script);
            console.log("emotion:", emotion);

            changeCatImage(emotion);

        } catch (error) {
            console.error("コメント生成/返信エラー:", error);
        }
    }

    async function generateSelfIntroduction(){
        try{
            addEventToQueue("generate_comment",1);
            const response = await fetch("/api/self-introduction");
            const data = await response.json();
            const script = data.script;
            console.log("script: ",script);

        } catch(error) {
            console.error("コメント生成/返信エラー:", error);
        }
    }

    async function generateNewsTalk(){
        try{
            addEventToQueue("generate_comment",1);
            const response = await fetch("/api/news-talk");
            const data = await response.json();
            const script = data.script;
            const emotion = data.emotion;
            console.log("script: ",script)
            console.log("emotion:", emotion);
            changeCatImage(emotion);

        }catch(error){
            console.error("コメント生成/返信エラー: ",error);
        }
    }

    async function generateWeatherTalk(){
        try{
            addEventToQueue("generate_comment",1);
            const response = await fetch("/api/weather-talk");
            const data = await response.json();
            const script = data.script;
            const emotion = data.emotion;
            console.log("script: ", script);
            console.log("emotion: ",emotion);
            changeCatImage(emotion);
        }catch(error){
            console.error("コメント生成/返信エラー:" ,error);
        }
    }

    const generateSuperChatBtn = document.getElementById("generateSuperChatBtn");
    const generateCommentBtn = document.getElementById("generateCommentBtn");
    const generateSelfIntroductionBtn = document.getElementById("generateSelfIntroductionBtn");
    const generateNewsTalkBtn = document.getElementById("generateNewsTalkBtn");
    const generateWeatherTalkBtn = document.getElementById("generateWeatherTalkBtn");

    generateSuperChatBtn.addEventListener("click", () => {
        enqueueEvent(
            "generate_superChat",
            100,
            generateSuperChat
        );
    });

    generateCommentBtn.addEventListener("click", () => {
        enqueueEvent(
            "generate_comment",
            2,
            generateCommentAutomatically
        );
    });

    generateSelfIntroductionBtn.addEventListener("click",() => {
        enqueueEvent(
            "generate_self_introduction",
            1,
            generateSelfIntroduction
        )
    });

    generateNewsTalkBtn.addEventListener("click",() => {
        enqueueEvent(
            "generage_news_talk",
            1,
            generateNewsTalk
        ) 
    });

    generateWeatherTalkBtn.addEventListener("click",() => {
        enqueueEvent(
            "generate_weather_talk",
            1,
            generateWeatherTalk
        )
    })



    const eventQueue = document.getElementById("eventQueue");
    function addEventToQueue(type, priority) {
        const item = document.createElement("div");

        item.textContent =
            `[${priority}] ${type}`;

        eventQueue.appendChild(item);

        eventQueue.scrollTop =
            eventQueue.scrollHeight;
    }

    function enqueueEvent(type, priority, handler) {
        const event = {type,priority,handler};
        eventQueueData.push(event);
        eventQueueData.sort((a, b) => b.priority - a.priority);
        renderEventQueue();
        processQueue();
    }

    function renderEventQueue() {
        eventQueue.innerHTML = "";
        eventQueueData.forEach(event => {
            const item = document.createElement("div");
            item.textContent = `[${event.priority}] ${event.type}`;
            eventQueue.appendChild(item);
        });
    }

    async function processQueue() {
        if (isProcessing) {return;}
        isProcessing = true;
        while (eventQueueData.length > 0) {
            const event = eventQueueData.shift();
            renderEventQueue();
            try {
                await event.handler();
            } catch (error) {
                console.error(error);
            }
        }
        isProcessing = false;
    }


    const sendUserCommentBtn = document.getElementById("sendUserCommentBtn");

    sendUserCommentBtn.addEventListener("click", async () => {
        const username = document.getElementById("usernameInput").value;
        const message = document.getElementById("messageInput").value;

        if (!username || !message) return;

        try {
            addCommentToUI({
                username: username,
                text: message,
                time: "now"
            });

            const response = await fetch("/api/user-comment/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username,
                    message
                })
            });

            const data = await response.json();

            const reply = data.reply;

            console.log("AI reply:", reply.script);

            changeCatImage(reply.emotion);

        } catch (err) {
            console.error("user comment error:", err);
        }
    });

    startBlinkLoop();
});