const apiBase = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export function apiUrl(path: string): string {
  return `${apiBase}${path}`;
}

export async function postAction(path: string): Promise<void> {
  await fetch(apiUrl(path), {
    method: "POST",
  });
}

export async function postJson<TResponse>(path: string, body: unknown): Promise<TResponse> {
  const response = await fetch(apiUrl(path), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return (await response.json()) as TResponse;
}

export async function setSimulationSpeed(speedLabel: string): Promise<void> {
  await postJson("/api/sim/speed", { speed_label: speedLabel });
}

export async function saveSimulationSnapshot(): Promise<void> {
  await postAction("/api/sim/snapshot/save");
}

export async function loadSimulationSnapshot(): Promise<void> {
  await postAction("/api/sim/snapshot/load");
}

export async function jumpToSimulationBookmark(bookmarkKey: string): Promise<void> {
  await postJson("/api/sim/bookmark", { bookmark_key: bookmarkKey });
}

export function websocketUrl(): string {
  return apiBase.replace("http://", "ws://").replace("https://", "wss://") + "/ws/state";
}
