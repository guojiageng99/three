const apiBase = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export function apiUrl(path: string): string {
  return `${apiBase}${path}`;
}

export async function postAction(path: string): Promise<void> {
  await fetch(apiUrl(path), {
    method: "POST",
  });
}

export function websocketUrl(): string {
  return apiBase.replace("http://", "ws://").replace("https://", "wss://") + "/ws/state";
}

