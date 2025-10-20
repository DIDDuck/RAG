
export const development = true;
export const production = !development;
export let backendUrl: string;

if (development) {
    backendUrl = "http://127.0.0.1:5000/chat"
}

if (production) {
    backendUrl = window.location.origin +  "/api/chat"
} 