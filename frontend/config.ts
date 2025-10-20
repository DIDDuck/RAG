
export const development = true;
export const production = !development;
export let backendUrl: string;

if (development) {
    backendUrl = "http://localhost:5000"
}

if (production) {
    backendUrl = window.location.origin +  "/api/rag_response"
} 