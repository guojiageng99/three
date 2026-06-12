import { WorldState } from "@/lib/types";

const apiBase = (process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000").trim();

export class ApiRequestError extends Error {
  status: number;
  detailStatus?: string;

  constructor(message: string, status: number, detailStatus?: string) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.detailStatus = detailStatus;
  }
}

export function apiUrl(path: string): string {
  return `${apiBase}${path}`;
}

async function readErrorMessage(response: Response): Promise<{ message: string; detailStatus?: string }> {
  try {
    const payload = (await response.json()) as { detail?: string | { message?: string; status?: string } };
    if (typeof payload.detail === "string") {
      return { message: payload.detail };
    }
    if (payload.detail && typeof payload.detail === "object") {
      const message = payload.detail.message?.trim();
      const detailStatus = payload.detail.status?.trim();
      if (message) {
        return { message, detailStatus };
      }
    }
  } catch {
    // ignore parse errors
  }
  return { message: `Request failed: ${response.status}` };
}

export async function getSimulationState(): Promise<WorldState> {
  const response = await fetch(apiUrl("/api/state"), {
    cache: "no-store",
  });
  if (!response.ok) {
    const { message } = await readErrorMessage(response);
    throw new ApiRequestError(message, response.status);
  }
  return (await response.json()) as WorldState;
}

export async function postAction(path: string): Promise<void> {
  const response = await fetch(apiUrl(path), {
    method: "POST",
  });
  if (!response.ok) {
    const { message, detailStatus } = await readErrorMessage(response);
    throw new ApiRequestError(message, response.status, detailStatus);
  }
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
    const { message, detailStatus } = await readErrorMessage(response);
    throw new ApiRequestError(message, response.status, detailStatus);
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
