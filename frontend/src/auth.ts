
const STORED_ACCESS_TOKEN = "accessToken";


export function saveAccessToken(token: string) {
    localStorage.setItem(STORED_ACCESS_TOKEN, token);
}


export function deleteAccessToken() {
    localStorage.removeItem(STORED_ACCESS_TOKEN);
}


export function withAccessTokenHeader(headers: Record<string, string>): Record<string, string> {
    const storedAccessToken = localStorage.getItem(STORED_ACCESS_TOKEN);
    if (storedAccessToken == null) return headers;
    else {
        headers["X-Token"] = storedAccessToken;
        return headers;
    }
}
