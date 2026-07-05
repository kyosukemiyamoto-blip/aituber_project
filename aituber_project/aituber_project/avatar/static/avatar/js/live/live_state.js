const INITIAL_STATE = Object.freeze({
    initialized: false,
    liveInfo: null,
    pollingStarted: false,
    pollingReady: false,
    broadcastStarted: false,
    liveEnded: false
});


export const liveState = {
    ...INITIAL_STATE
};


export function resetLiveState() {
    Object.assign(liveState, INITIAL_STATE);
}
