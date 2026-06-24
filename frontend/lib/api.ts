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

  const data = await response.json();
  return data as ChatResponse;
}

export type ClassifierDebugResponse = {
  user_message: string;

  ml_issue_available: boolean;
  ml_issue_category?: string | null;
  ml_issue_confidence?: number | null;
  ml_issue_top_categories: string[];
  ml_issue_top_scores: number[];

  rule_issue_category: string;
  rule_issue_confidence: number;
  rule_issue_matched_keywords: string[];

  final_issue_category_before_correction: string;
  final_issue_category_after_correction: string;
  category_correction_reasons: string[];

  ml_urgency_available: boolean;
  ml_urgency?: string | null;
  ml_urgency_confidence?: number | null;
  ml_urgency_top_urgencies: string[];
  ml_urgency_top_scores: number[];

  rule_urgency: string;
  rule_urgency_confidence: number;
  rule_urgency_reasons: string[];

  final_urgency_before_correction: string;
  final_urgency_after_correction: string;
  urgency_correction_reasons: string[];

  retrieved_sources: SourceSnippet[];
};

export async function debugChatMessage(
  message: string
): Promise<ClassifierDebugResponse> {
  const response = await fetch(`${API_BASE_URL}/chat/debug`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error(`Debug API error: ${response.status}`);
  }

  const data = await response.json();
  return data as ClassifierDebugResponse;
}