// VTube Studio API Integration
// VTube Studio API Documentation: https://github.com/DenchiSoft/VTubeStudio

export class VTubeStudioAPI {
    constructor(url = "ws://localhost:8001") {
        this.url = url;
        this.ws = null;

        this.connected = false;
        this.authenticated = false;
        this.authToken = null;

        this.pluginName = "AITuber Live System";
        this.pluginDeveloper = "AITuber";

        this.messageId = 0;
        this.callbacks = new Map();

        this.currentModel = null;
        this.availableParameters = [];
    }

    // ==============================
    // Utility
    // ==============================
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    clamp(value, min = 0.0, max = 1.0) {
        return Math.max(min, Math.min(max, value));
    }

    // ==============================
    // WebSocket Connection
    // ==============================
    connect() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(this.url);

                this.ws.onopen = () => {
                    console.log("VTube Studio WebSocket接続成功");
                    this.connected = true;
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    this.handleMessage(event.data);
                };

                this.ws.onerror = (error) => {
                    console.error("VTube Studio WebSocket エラー:", error);
                    this.connected = false;
                    reject(error);
                };

                this.ws.onclose = () => {
                    console.log("VTube Studio WebSocket接続終了");
                    this.connected = false;
                    this.authenticated = false;
                };

            } catch (error) {
                reject(error);
            }
        });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        this.connected = false;
        this.authenticated = false;
    }

    isConnected() {
        return this.connected && this.authenticated;
    }

    // ==============================
    // Message Handling
    // ==============================
    sendMessage(messageType, data = {}) {
        return new Promise((resolve, reject) => {
            if (!this.connected || !this.ws) {
                reject(new Error("VTube Studioに接続されていません"));
                return;
            }

            const requestID = `msg_${this.messageId++}`;

            const message = {
                apiName: "VTubeStudioPublicAPI",
                apiVersion: "1.0",
                requestID: requestID,
                messageType: messageType,
                data: data
            };

            this.callbacks.set(requestID, { resolve, reject });

            try {
                this.ws.send(JSON.stringify(message));
            } catch (error) {
                this.callbacks.delete(requestID);
                reject(error);
                return;
            }

            setTimeout(() => {
                if (this.callbacks.has(requestID)) {
                    this.callbacks.delete(requestID);
                    reject(new Error(`リクエストタイムアウト: ${messageType}`));
                }
            }, 10000);
        });
    }

    handleMessage(rawData) {
        try {
            const message = JSON.parse(rawData);
            const requestID = message.requestID;

            if (!requestID || !this.callbacks.has(requestID)) {
                return;
            }

            const { resolve, reject } = this.callbacks.get(requestID);
            this.callbacks.delete(requestID);

            if (message.data && message.data.errorID) {
                reject(new Error(message.data.message || "Unknown VTube Studio API error"));
                return;
            }

            resolve(message.data);

        } catch (error) {
            console.error("VTube Studioメッセージ解析エラー:", error);
        }
    }

    // ==============================
    // Authentication
    // ==============================
    async requestAuthToken() {
        try {
            const response = await this.sendMessage("AuthenticationTokenRequest", {
                pluginName: this.pluginName,
                pluginDeveloper: this.pluginDeveloper
            });

            this.authToken = response.authenticationToken;
            localStorage.setItem("vtubeStudioAuthToken", this.authToken);

            console.log("VTube Studio認証トークン取得成功");
            return this.authToken;

        } catch (error) {
            console.error("VTube Studio認証トークン取得エラー:", error);
            throw error;
        }
    }

    async authenticate() {
        try {
            const savedToken = localStorage.getItem("vtubeStudioAuthToken");

            if (savedToken) {
                this.authToken = savedToken;
            }

            if (!this.authToken) {
                await this.requestAuthToken();
            }

            const response = await this.sendMessage("AuthenticationRequest", {
                pluginName: this.pluginName,
                pluginDeveloper: this.pluginDeveloper,
                authenticationToken: this.authToken
            });

            this.authenticated = response.authenticated;

            if (!this.authenticated) {
                localStorage.removeItem("vtubeStudioAuthToken");
                this.authToken = null;

                await this.requestAuthToken();
                return await this.authenticate();
            }

            console.log("VTube Studio認証成功");
            return true;

        } catch (error) {
            console.error("VTube Studio認証エラー:", error);
            throw error;
        }
    }

    // ==============================
    // Model / Parameters
    // ==============================
    async getCurrentModel() {
        try {
            const response = await this.sendMessage("CurrentModelRequest");
            this.currentModel = response;
            return response;

        } catch (error) {
            console.error("VTube Studioモデル情報取得エラー:", error);
            throw error;
        }
    }

    async getAvailableParameters() {
        try {
            const response = await this.sendMessage("InputParameterListRequest");
            this.availableParameters = response.defaultParameters || [];
            return this.availableParameters;

        } catch (error) {
            console.error("VTube Studioパラメータ一覧取得エラー:", error);
            throw error;
        }
    }

    async setParameterValue(parameterId, value, weight = 1.0) {
        try {
            await this.sendMessage("InjectParameterDataRequest", {
                parameterValues: [
                    {
                        id: parameterId,
                        value: value,
                        weight: weight
                    }
                ]
            });

        } catch (error) {
            console.error(`VTube Studioパラメータ設定エラー: ${parameterId}`, error);
            throw error;
        }
    }

    async setMultipleParameters(parameters) {
        try {
            const parameterValues = parameters.map(param => ({
                id: param.id,
                value: param.value,
                weight: param.weight ?? 1.0
            }));

            await this.sendMessage("InjectParameterDataRequest", {
                parameterValues: parameterValues
            });

        } catch (error) {
            console.error("VTube Studio複数パラメータ設定エラー:", error);
            throw error;
        }
    }

    // ==============================
    // Mouth / Lip Sync
    // ==============================
    async setMouthOpen(value, weight = 1.0) {
        const mouthValue = this.clamp(Number(value) || 0.0, 0.0, 1.0);

        try {
            await this.setParameterValue("MouthOpen", mouthValue, weight);
        } catch (error) {
            console.error("VTube Studio口の開閉エラー:", error);
        }
    }

    getMouthOpenValue(segment) {
        /*
            新方式:
              { mouth: 0.45, duration: 0.08 }

            旧方式:
              { vowel: "a", duration: 0.12 }
        */

        if (typeof segment.mouth === "number") {
            return this.clamp(segment.mouth, 0.0, 1.0);
        }

        const vowel = segment.vowel;

        const openValues = {
            a: 0.85,
            i: 0.35,
            u: 0.45,
            e: 0.55,
            o: 0.65,
            N: 0.20,
            n: 0.20,
            pau: 0.0,
            cl: 0.0,
            sil: 0.0
        };

        return this.clamp(openValues[vowel] ?? 0.0, 0.0, 1.0);
    }

    normalizeLipSegment(segment) {
        const mouth = this.getMouthOpenValue(segment);

        const rawDuration = Number(segment.duration);
        const duration = Number.isFinite(rawDuration) && rawDuration > 0
            ? rawDuration
            : 0.08;

        return {
            mouth: mouth,
            duration: duration,
            viseme_id: segment.viseme_id ?? null,
            vowel: segment.vowel ?? null
        };
    }

    async performLipSync(lipData, voiceSpeed = 1.0) {
        if (!Array.isArray(lipData) || lipData.length === 0) {
            console.warn("lipData is empty");
            await this.setMouthOpen(0.0);
            return;
        }

        const speed = Number.isFinite(Number(voiceSpeed)) && Number(voiceSpeed) > 0
            ? Number(voiceSpeed)
            : 1.0;

        try {
            for (const rawSegment of lipData) {
                const segment = this.normalizeLipSegment(rawSegment);

                await this.setMouthOpen(segment.mouth);

                const waitMs = Math.max(15, (segment.duration * 1000) / speed);
                await this.sleep(waitMs);
            }

            await this.setMouthOpen(0.0);

        } catch (error) {
            console.error("VTube Studioリップシンクエラー:", error);

            try {
                await this.setMouthOpen(0.0);
            } catch (_) {
                // ignore
            }
        }
    }

    // ==============================
    // Hotkeys / Expressions
    // ==============================
    async triggerHotkey(hotkeyID) {
        try {
            await this.sendMessage("HotkeyTriggerRequest", {
                hotkeyID: hotkeyID
            });

        } catch (error) {
            console.error("VTube Studioホットキートリガーエラー:", error);
            throw error;
        }
    }

    async getAvailableHotkeys() {
        try {
            const response = await this.sendMessage("HotkeysInCurrentModelRequest");
            return response.availableHotkeys || [];

        } catch (error) {
            console.error("VTube Studioホットキー一覧取得エラー:", error);
            throw error;
        }
    }

    async setExpression(expressionName) {
        try {
            const hotkeys = await this.getAvailableHotkeys();

            const targetName = String(expressionName || "normal").toLowerCase();

            const expressionHotkey = hotkeys.find(hotkey => {
                const hotkeyName = String(hotkey.name || "").toLowerCase();
                return hotkeyName.includes(targetName);
            });

            if (!expressionHotkey) {
                console.warn(`表情 "${expressionName}" が見つかりません`);
                return;
            }

            await this.triggerHotkey(expressionHotkey.hotkeyID);

        } catch (error) {
            console.error("VTube Studio表情変更エラー:", error);
        }
    }

    async setEmotionExpression(emotion) {
        const emotionMap = {
            NORMAL: "normal",
            DEFAULT: "normal",
            HAPPY: "happy",
            SAD: "sad",
            ANGRY: "angry",
            SURPRISED: "surprised"
        };

        const normalizedEmotion = String(emotion || "normal").toUpperCase();
        const expressionName = emotionMap[normalizedEmotion] || "normal";

        await this.setExpression(expressionName);
    }

    // ==============================
    // Motions
    // ==============================
    async playRandomMotion(motionNames) {
        try {
            const hotkeys = await this.getAvailableHotkeys();

            const motionHotkeys = hotkeys.filter(hotkey => {
                const hotkeyName = String(hotkey.name || "").toLowerCase();

                return motionNames.some(name => {
                    return hotkeyName.includes(String(name).toLowerCase());
                });
            });

            if (motionHotkeys.length === 0) {
                console.warn("指定されたモーションが見つかりません:", motionNames);
                return;
            }

            const randomHotkey = motionHotkeys[
                Math.floor(Math.random() * motionHotkeys.length)
            ];

            console.log(`ランダムモーション再生: ${randomHotkey.name}`);

            await this.triggerHotkey(randomHotkey.hotkeyID);

        } catch (error) {
            console.error("VTube Studioランダムモーション再生エラー:", error);
        }
    }
}


// ==============================
// VTube Studio Manager
// ==============================
export class VTubeStudioManager {
    constructor(url = "ws://localhost:8001") {
        this.api = new VTubeStudioAPI(url);
        this.initialized = false;
    }

    async initialize() {
        try {
            await this.api.connect();
            await this.api.authenticate();
            await this.api.getCurrentModel();
            await this.api.getAvailableParameters();

            this.initialized = true;

            console.log("VTube Studio Manager初期化完了");
            return true;

        } catch (error) {
            console.error("VTube Studio Manager初期化エラー:", error);
            throw error;
        }
    }

    async changeExpression(emotion) {
        if (!this.initialized) {
            console.warn("VTube Studio Managerが初期化されていません");
            return;
        }

        await this.api.setEmotionExpression(emotion);
    }

    async lipSync(lipData, voiceSpeed = 1.0) {
        if (!this.initialized) {
            console.warn("VTube Studio Managerが初期化されていません");
            return;
        }

        await this.api.performLipSync(lipData, voiceSpeed);
    }

    async setMouthOpen(value) {
        if (!this.initialized) {
            console.warn("VTube Studio Managerが初期化されていません");
            return;
        }

        await this.api.setMouthOpen(value);
    }

    async playRandomMotion(motionNames) {
        if (!this.initialized) {
            console.warn("VTube Studio Managerが初期化されていません");
            return;
        }

        await this.api.playRandomMotion(motionNames);
    }

    getModelInfo() {
        return this.api.currentModel;
    }

    getAvailableParameters() {
        return this.api.availableParameters;
    }

    isConnected() {
        return this.api.isConnected();
    }

    disconnect() {
        this.api.disconnect();
        this.initialized = false;
    }
}