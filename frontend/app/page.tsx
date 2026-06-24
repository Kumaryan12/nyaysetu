"use client";

import { ChangeEvent, useState } from "react";
import { ChatResponse, SourceSnippet, sendChatMessage } from "@/lib/api";

const examples = [
  "How can I get free legal aid?",
  "My employer has not paid my salary for three months.",
  "A loan app is threatening to share my photos with contacts.",
  "My public grievance was closed without resolution. What can I do next?",
];

const coverageAreas = [
  "Legal aid",
  "Consumer complaints",
  "Police and cybercrime",
  "Labour issues",
  "Public grievances",
  "Women safety",
];

const emergencyNotes = [
  "If someone is in immediate danger, contact local emergency services first.",
  "Keep screenshots, messages, IDs, receipts, notices, and dates together.",
  "For formal action, verify deadlines with the relevant authority or lawyer.",
];

function urgencyClass(urgency: string) {
  if (urgency === "High")
    return "border-red-400/40 bg-red-500/10 text-red-200 ring-red-500/10";
  if (urgency === "Medium")
    return "border-amber-400/40 bg-amber-500/10 text-amber-200 ring-amber-500/10";
  if (urgency === "Low")
    return "border-emerald-400/40 bg-emerald-500/10 text-emerald-200 ring-emerald-500/10";
  return "border-stone-500/40 bg-stone-500/10 text-stone-200 ring-stone-500/10";
}

function FieldBadge({
  label,
  value,
  variant,
}: {
  label: string;
  value: string;
  variant?: string;
}) {
  return (
    <div className="rounded-lg border border-[#3a3129] bg-[#15120f] p-4 shadow-[0_18px_50px_rgba(0,0,0,0.24)]">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#a99f92]">
        {label}
      </p>
      {variant ? (
        <span
          className={`mt-3 inline-flex rounded-full border px-3 py-1.5 text-sm font-semibold ring-4 ${variant}`}
        >
          {value || "Unknown"}
        </span>
      ) : (
        <p className="mt-2 text-lg font-semibold text-[#f6efe5]">
          {value || "Unknown"}
        </p>
      )}
    </div>
  );
}

function ContentSection({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-lg border border-[#3a3129] bg-[#15120f] p-5 shadow-[0_18px_50px_rgba(0,0,0,0.24)]">
      <div className="mb-4">
        <h2 className="text-base font-semibold text-[#f6efe5]">{title}</h2>
        {description && (
          <p className="mt-1 text-sm leading-6 text-[#a99f92]">
            {description}
          </p>
        )}
      </div>
      {children}
    </section>
  );
}

function SourceCard({ source }: { source: SourceSnippet }) {
  const details = [
    source.publisher,
    source.domain,
    source.jurisdiction,
    source.source_type,
  ].filter(Boolean);

  return (
    <article className="rounded-lg border border-[#342b24] bg-[#1b1713] p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-sm font-semibold text-[#f6efe5]">
            {source.title || "Reference"}
          </h3>
          {details.length > 0 && (
            <p className="mt-1 text-xs leading-5 text-[#a99f92]">
              {details.join(" / ")}
            </p>
          )}
        </div>

        {source.url && (
          <a
            href={source.url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex w-fit items-center rounded-md border border-[#55c7a4]/50 bg-[#10221d] px-3 py-1.5 text-xs font-semibold text-[#9af0d3] transition hover:border-[#8de4c8] hover:bg-[#15352c]"
          >
            Open source
          </a>
        )}
      </div>

      {source.text && (
        <p className="mt-3 line-clamp-4 text-sm leading-6 text-[#bdb2a5]">
          {source.text}
        </p>
      )}
    </article>
  );
}

export default function Home() {
  const [message, setMessage] = useState("");
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleMessageChange(e: ChangeEvent<HTMLTextAreaElement>) {
    setMessage(e.target.value);
  }

  async function handleSubmit() {
    if (!message.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const chatData = await sendChatMessage(message);
      setResult(chatData);
    } catch {
      setError(
        "We could not reach the guidance service. Please check that the local server is running and try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#090807] text-[#f6efe5]">
      <div className="border-b border-[#342b24] bg-[#0d0b0a]/95">
        <header className="mx-auto flex max-w-7xl flex-col gap-3 px-5 py-6 sm:px-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#55c7a4]">
              India legal guidance
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-[#fff7ec]">
              NyayaSetu
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-[#bdb2a5]">
              Clear first-step guidance for legal aid, public services, and
              rights-related issues.
            </p>
          </div>

          <p className="max-w-sm text-sm leading-6 text-[#a99f92] lg:text-right">
            Built for practical next steps, source checking, and safer decisions
            before you contact an office, lawyer, or helpdesk.
          </p>
        </header>
      </div>

      <div className="mx-auto grid max-w-7xl gap-6 px-5 py-7 sm:px-6 lg:grid-cols-[minmax(0,1fr)_350px]">
        <section className="space-y-5">
          <section className="overflow-hidden rounded-lg border border-[#3a3129] bg-[#15120f] shadow-[0_24px_80px_rgba(0,0,0,0.34)]">
            <div className="border-b border-[#3a3129] bg-[#1c1813] px-5 py-5">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <h2 className="text-xl font-semibold tracking-tight text-[#fff7ec]">
                    Tell us what happened
                  </h2>
                  <p className="mt-2 max-w-2xl text-sm leading-6 text-[#bdb2a5]">
                    Share the facts, location, dates, people involved, and the
                    outcome you need.
                  </p>
                </div>
                <span className="w-fit rounded-full border border-[#c49a58]/40 bg-[#c49a58]/10 px-3 py-1.5 text-xs font-semibold text-[#f2d39b]">
                  General information
                </span>
              </div>
            </div>

            <div className="p-5">
              <label
                htmlFor="issue"
                className="text-sm font-semibold text-[#e8ded1]"
              >
                Your situation
              </label>
              <textarea
                id="issue"
                className="mt-2 min-h-48 w-full resize-none rounded-lg border border-[#463a30] bg-[#0d0b0a] px-4 py-3 text-sm leading-6 text-[#fff7ec] outline-none transition placeholder:text-[#74685c] focus:border-[#55c7a4] focus:bg-[#11100e] focus:ring-4 focus:ring-[#55c7a4]/10"
                placeholder="Example: My employer has not paid my salary for three months. I have messages and an appointment letter. What should I do?"
                value={message}
                onChange={handleMessageChange}
              />

              <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <p className="max-w-2xl text-xs leading-5 text-[#a99f92]">
                  Avoid entering passwords, OTPs, bank details, or private
                  identity numbers.
                </p>

                <button
                  onClick={handleSubmit}
                  disabled={loading || !message.trim()}
                  className="inline-flex items-center justify-center rounded-md bg-[#55c7a4] px-5 py-2.5 text-sm font-semibold text-[#07100d] shadow-[0_14px_30px_rgba(85,199,164,0.18)] transition hover:bg-[#7ee0c1] disabled:cursor-not-allowed disabled:bg-[#3a3129] disabled:text-[#8e8377]"
                >
                  {loading ? "Preparing guidance..." : "Get guidance"}
                </button>
              </div>

              {error && (
                <p className="mt-4 rounded-lg border border-red-400/30 bg-red-500/10 p-3 text-sm leading-6 text-red-200">
                  {error}
                </p>
              )}
            </div>
          </section>

          {!result && (
            <section className="grid gap-3 md:grid-cols-2">
              {examples.map((example) => (
                <button
                  key={example}
                  onClick={() => setMessage(example)}
                  className="rounded-lg border border-[#342b24] bg-[#15120f] p-4 text-left text-sm leading-6 text-[#d6cbbd] shadow-[0_14px_40px_rgba(0,0,0,0.22)] transition hover:border-[#55c7a4]/60 hover:bg-[#1a1713]"
                >
                  {example}
                </button>
              ))}
            </section>
          )}

          {result && (
            <>
              <div className="grid gap-4 md:grid-cols-2">
                <FieldBadge
                  label="Issue area"
                  value={result.category || "Unknown"}
                />
                <FieldBadge
                  label="Urgency"
                  value={result.urgency || "Unknown"}
                  variant={urgencyClass(result.urgency)}
                />
              </div>

              <ContentSection
                title="Guidance"
                description="A practical summary based on the details you shared."
              >
                <p className="whitespace-pre-line text-sm leading-7 text-[#d6cbbd]">
                  {result.simple_answer}
                </p>
              </ContentSection>

              {result.next_steps?.length > 0 && (
                <ContentSection title="Next steps">
                  <ol className="space-y-3">
                    {result.next_steps.map((step, index) => (
                      <li
                        key={index}
                        className="grid grid-cols-[2rem_1fr] gap-3 rounded-lg border border-[#342b24] bg-[#1b1713] px-4 py-3 text-sm leading-6 text-[#d6cbbd]"
                      >
                        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#55c7a4] text-xs font-semibold text-[#07100d]">
                          {index + 1}
                        </span>
                        <span className="pt-1">{step}</span>
                      </li>
                    ))}
                  </ol>
                </ContentSection>
              )}

              {result.documents_or_details_needed?.length > 0 && (
                <ContentSection
                  title="Documents and details"
                  description="Keep these ready before contacting an authority, lawyer, or helpdesk."
                >
                  <div className="flex flex-wrap gap-2">
                    {result.documents_or_details_needed.map((doc, index) => (
                      <span
                        key={index}
                        className="rounded-full border border-[#c49a58]/40 bg-[#c49a58]/10 px-3 py-1.5 text-xs font-semibold text-[#f2d39b]"
                      >
                        {doc}
                      </span>
                    ))}
                  </div>
                </ContentSection>
              )}

              <ContentSection
                title="References"
                description="Relevant public information that may help you verify the guidance."
              >
                {result.sources.length === 0 ? (
                  <p className="text-sm text-[#a99f92]">
                    No references were found for this question.
                  </p>
                ) : (
                  <div className="space-y-3">
                    {result.sources.map((source, index) => (
                      <SourceCard key={index} source={source} />
                    ))}
                  </div>
                )}
              </ContentSection>

              {result.disclaimer && (
                <p className="rounded-lg border border-[#3a3129] bg-[#15120f] p-4 text-sm leading-6 text-[#a99f92] shadow-[0_18px_50px_rgba(0,0,0,0.24)]">
                  {result.disclaimer}
                </p>
              )}
            </>
          )}
        </section>

        <aside className="space-y-5">
          <section className="rounded-lg border border-[#3a3129] bg-[#15120f] p-5 shadow-[0_18px_50px_rgba(0,0,0,0.24)]">
            <h2 className="text-sm font-semibold text-[#fff7ec]">
              Supported areas
            </h2>
            <div className="mt-4 grid gap-2">
              {coverageAreas.map((area) => (
                <div
                  key={area}
                  className="flex items-center gap-3 rounded-md border border-[#342b24] bg-[#1b1713] px-3 py-2"
                >
                  <span className="h-2 w-2 rounded-full bg-[#55c7a4]" />
                  <span className="text-sm text-[#d6cbbd]">{area}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-lg border border-[#3a3129] bg-[#15120f] p-5 shadow-[0_18px_50px_rgba(0,0,0,0.24)]">
            <h2 className="text-sm font-semibold text-[#fff7ec]">
              Before you proceed
            </h2>
            <div className="mt-4 space-y-3">
              {emergencyNotes.map((note) => (
                <p
                  key={note}
                  className="rounded-md border border-[#c49a58]/30 bg-[#c49a58]/10 px-3 py-2 text-sm leading-6 text-[#f2d39b]"
                >
                  {note}
                </p>
              ))}
            </div>
          </section>
        </aside>
      </div>
    </main>
  );
}
