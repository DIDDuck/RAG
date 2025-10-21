
export const development = true;
export const production = !development;
export let backendChatUrl: string;
export let backendFileListUrl: string;

if (development) {
    backendChatUrl = "http://127.0.0.1:5000/chat";
    backendFileListUrl = "http://127.0.0.1:5000/files";
}

if (production) {
    backendChatUrl = window.location.origin +  "/api/chat";
    backendFileListUrl = window.location.origin + "/api/files"
} 