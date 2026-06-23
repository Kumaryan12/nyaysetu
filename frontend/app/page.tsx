"use client";

import { useState } from "react";
import { ChatResponse, sendChatMessage } from "@/lib/api";

function urgencyClass(urgency: string) {
  if (urgency === "High") return "bg-red-100 text-red-700 border-red-300";
  if (urgency === "Medium") return "bg-yellow-100 text-yellow-700 border-yellow-300";
  if (urgency === "Low") return "bg-green-100 text-green-700 border-green-300";
  return "bg-gray-100 text-gray-700 border-gray-300";
}

export default function Home() {
  const [message, setMessage] = useState("");
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit() {
    if (!message.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await sendChatMessage(message);
      setResult(data);
    } catch (err) {
      setError("Could not connect to backend. Make sure FastAPI is running on port 8000.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto max-w-5xl px-6 py-10">
        <div className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight">NyayaSetu</h1>
          <p className="mt-3 max-w-2xl text-slate-600">
            A source-grounded legal-aid and public-service grievance assistant for Indian citizens.
          </p>
        </div>

        <div className="rounded-2xl border bg-white p-5 shadow-sm">
          <label className="mb-2 block text-sm font-medium text-slate-700">
            Describe your issue
          </label>

          <textarea
            className="h-36 w-full rounded-xl border border-slate-300 p-4 outline-none focus:border-slate-500"
            placeholder="Example: My employer has not paid my salary for three months. What should I do?"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="mt-4 rounded-xl bg-slate-900 px-5 py-3 font-medium text-white disabled:opacity-60"
          >
            {loading ? "Analyzing..." : "Ask NyayaSetu"}
          </button>

          {error && (
            <p className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-red-700">
              {error}
            </p>
          )}
        </div>

        {result && (
          <div className="mt-8 grid gap-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl border bg-white p-5 shadow-sm">
                <p className="text-sm text-slate-500">Detected Category</p>
                <p className="mt-1 text-2xl font-semibold">
                  {result.category || "Unknown"}
                </p>
              </div>

              <div className="rounded-2xl border bg-white p-5 shadow-sm">
                <p className="text-sm text-slate-500">Urgency</p>
                <span
                  className={`mt-2 inline-block rounded-full border px-4 py-2 text-sm font-semibold ${urgencyClass(
                    result.urgency
                  )}`}
                >
                  {result.urgency}
                </span>
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Simple Answer</h2>
              <p className="mt-3 whitespace-pre-line leading-7 text-slate-700">
                {result.simple_answer}
              </p>
            </div>

            {result.next_steps.length > 0 && (
              <div className="rounded-2xl border bg-white p-5 shadow-sm">
                <h2 className="text-xl font-semibold">Next Steps</h2>
                <ul className="mt-3 list-disc space-y-2 pl-6 text-slate-700">
                  {result.next_steps.map((step, index) => (
                    <li key={index}>{step}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.documents_or_details_needed.length > 0 && (
              <div className="rounded-2xl border bg-white p-5 shadow-sm">
                <h2 className="text-xl font-semibold">Documents / Details Needed</h2>
                <ul className="mt-3 list-disc space-y-2 pl-6 text-slate-700">
                  {result.documents_or_details_needed.map((doc, index) => (
                    <li key={index}>{doc}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Sources Used</h2>

              {result.sources.length === 0 ? (
                <p className="mt-3 text-slate-600">No sources retrieved.</p>
              ) : (
                <div className="mt-4 space-y-4">
                  {result.sources.map((source, index) => (
                    <div key={index} className="rounded-xl border bg-slate-50 p-4">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-semibold">{source.title}</p>
                        {source.score !== null && source.score !== undefined && (
                          <span className="rounded-full bg-white px-2 py-1 text-xs text-slate-500">
                            score: {source.score.toFixed(2)}
                          </span>
                        )}
                      </div>

                      {source.url && (
                        <a
                          href={source.url}
                          target="_blank"
                          className="mt-1 block text-sm text-blue-600 underline"
                        >
                          Open official source
                        </a>
                      )}

                      <p className="mt-3 line-clamp-4 text-sm leading-6 text-slate-600">
                        {source.text}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <p className="rounded-xl border bg-white p-4 text-sm text-slate-500">
              {result.disclaimer}
            </p>
          </div>
        )}
      </section>
    </main>
  );
}