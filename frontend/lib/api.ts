export type SourceSnippet = {
  title: string;
  source_type: string;
  url?: string | null;
  text: string;
  score?: number | null;
};

export type ChatResponse = {
  category: string | null;
  urgency: "Low" | "Medium" | "High" | "Unknown";
  simple_answer: string;
  next_steps: string[];
  documents_or_details_needed: string[];
  disclaimer: string;
  sources: SourceSnippet[];
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}