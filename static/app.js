const DRAWERS = [
  // Every example is a test-set question the final run answered fully correctly (eval/results/results.json).
  { name: "Time off", questions: ["How much notice should I give my manager before taking PTO?", "How long is GitLab's parental leave, and by when do I have to use it?"] },
  { name: "Money & travel", questions: ["Can I expense a coworking space, and what is the limit?", "How much can I expense for internet access while traveling?"] },
  { name: "Benefits & equity", questions: ["When does my US medical coverage end after I leave GitLab?", "How long do I have to exercise my vested stock options after leaving GitLab?"] },
  { name: "Not held in this collection", notHeld: true, questions: ["What is the dress code for customer meetings?", "Does GitLab offer a four-day work week?"] },
];
const EXT = '<svg class="ext" aria-hidden="true" viewBox="0 0 16 16" width="12" height="12"><path d="M6 3h7v7M13 3 4 12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const MIN_CHARS = 3, MAX_CHARS = 500, SLOW_AFTER_MS = 8000;

const $ = (s, root = document) => root.querySelector(s);
const thread = $("#thread"), form = $("#composer"), input = $("#q"), send = $("#send"), status = $("#status");
let busy = false, turnCount = 0;

const escapeHtml = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
// Card text without Markdown: list markers, headings, bold/italic asterisks and underscores.
const plain = (s) => s.replace(/^\s*(#+|[-*•]|\d+[.)])\s+/gm, "").replace(/(\*{1,2}|__)(\S.*?\S|\S)\1/g, "$2").replace(/\*/g, "").replace(/\s+/g, " ").trim();
const callNumber = (url) => url.split("/handbook/")[1].split("#")[0].replace(/\/$/, "").split("/").slice(-2).join(" / ").toUpperCase();

// Safe Markdown subset for answers: escape first, then bold, lists, paragraphs, and [n] card marks.
function renderAnswer(text, cited, turnId) {
  const inline = (s) => escapeHtml(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\s*\[(\d+)\]/g, (m, n) => cited.has(+n)
      ? ` <button type="button" class="mark" data-card="${turnId}-c${n}" aria-label="Pull card ${n}">${n}</button>` : "");
  return text.trim().split(/\n\s*\n/).map((block) => {
    const lines = block.split("\n");
    if (lines.every((l) => /^\s*([-*•]|\d+[.)])\s+/.test(l))) {
      const tag = /^\s*\d/.test(lines[0]) ? "ol" : "ul";
      return `<${tag}>${lines.map((l) => `<li>${inline(l.replace(/^\s*([-*•]|\d+[.)])\s+/, ""))}</li>`).join("")}</${tag}>`;
    }
    return `<p>${lines.map(inline).join("<br>")}</p>`;
  }).join("");
}

// Which sentence of a card supports the answer: the one sharing the most words with the sentences that cite it.
const STOP = new Set("that this with from have will your their there which about would could should these those than then they them what when where while into only also more most such each been were does".split(" "));
const words = (s) => new Set((s.toLowerCase().match(/[a-z0-9$€£%]+/g) || []).filter((w) => w.length > 3 && !STOP.has(w)));
function excerpt(cardText, citingText) {
  const sentences = plain(cardText).split(/(?<=[.!?])\s+/).filter(Boolean);
  const want = words(citingText);
  let best = 0, bestScore = -1;
  sentences.forEach((s, i) => {
    const score = [...words(s)].filter((w) => want.has(w)).length;
    if (score > bestScore) { best = i; bestScore = score; }
  });
  const before = sentences[best - 1] && sentences[best - 1].length < 220 ? escapeHtml(sentences[best - 1]) + " " : "";
  const after = sentences[best + 1] && sentences[best + 1].length < 220 ? " " + escapeHtml(sentences[best + 1]) : "";
  return `${before ? "… " + before : ""}<mark>${escapeHtml(sentences[best] || "")}</mark>${after ? after + " …" : ""}`;
}

function cardHtml(c, turnId, answerText) {
  const citing = answerText.split(/(?<=[.!?])\s+|\n/).filter((s) => s.includes(`[${c.n}]`)).join(" ") || answerText;
  return `<article class="card" id="${turnId}-c${c.n}" tabindex="-1" aria-label="Card ${c.n}: ${escapeHtml(c.title)}">
    <div class="call"><span>№ ${c.n}</span><span class="path">${escapeHtml(callNumber(c.url))}</span></div>
    <p class="card-title">${escapeHtml(plain(c.title))}</p>
    ${c.section ? `<p class="section">§ ${escapeHtml(plain(c.section))}</p>` : ""}
    <blockquote>${excerpt(c.text, citing)}</blockquote>
    <details><summary>Show the full card</summary><div class="full">${escapeHtml(c.text.replace(/(\*{1,2}|__)(\S.*?\S|\S)\1/g, "$2"))}</div></details>
    <a class="open" href="${escapeHtml(c.url)}" target="_blank" rel="noopener">Open in the handbook${EXT}</a>
  </article>`;
}

// Suggested questions not asked yet, so guidance is never lost after the first answer.
function chipsHtml() {
  const asked = new Set([...thread.querySelectorAll(".turn h2 .q")].map((h) => h.textContent));
  return DRAWERS.filter((d) => !d.notHeld).flatMap((d) => d.questions).filter((q) => !asked.has(q)).slice(0, 3)
    .map((q) => `<button type="button" class="chip ask-chip">${escapeHtml(q)}</button>`).join("");
}

function startTurn(question) {
  $("#welcome")?.setAttribute("hidden", "");
  $("#new-search").hidden = false;
  const id = `t${++turnCount}`;
  const el = document.createElement("article");
  el.className = "turn";
  el.id = id;
  el.innerHTML = `<div class="left"><h2><span class="sr-only">You asked: </span><span class="q">${escapeHtml(question)}</span></h2>
      <div class="body"><div class="waiting"><span class="bar" aria-hidden="true"></span><span class="wait-text">Searching the catalog…</span></div></div></div>
    <aside class="rail" aria-label="Cards pulled"></aside>`;
  thread.appendChild(el);
  el.scrollIntoView({ behavior: "smooth", block: "start" });
  return el;
}

async function ask(question) {
  question = question.trim();
  if (busy || !question) return;
  if (question.length < MIN_CHARS) { status.textContent = "Please ask a full question."; input.focus(); return; }
  busy = true; send.disabled = true;
  const turn = startTurn(question), body = $(".body", turn), rail = $(".rail", turn);
  const slow = setTimeout(() => {
    const t = $(".wait-text", turn);
    if (t) t.textContent = "Still working. Answers usually take 10 to 30 seconds on the free tier.";
  }, SLOW_AFTER_MS);
  try {
    const res = await fetch("/api/ask", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question }) });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Something went wrong. Please try again.");
    if (data.refused) {
      body.innerHTML = `<div class="not-held-card"><span class="stamp">Not held in this collection</span>
        <p>The 48 handbook pages behind this assistant don't answer that, so it won't guess. Try one of these instead:</p>
        <div class="chips">${chipsHtml()}</div></div>`;
      rail.innerHTML = `<h3>Cards pulled · 0</h3><div class="empty-card">No card in the catalog matches this question.</div>`;
      status.textContent = "Not held in this collection.";
    } else {
      const cited = new Set(data.citations.map((c) => c.n));
      body.innerHTML = `<div class="answer">${renderAnswer(data.answer, cited, turn.id)}</div>` +
        `<div class="next"><p>Try another</p><div class="chips">${chipsHtml()}</div></div>` +
        (data.backup_model ? `<p class="note">Answered by the smaller backup model (gpt-oss-20b) because the main model's free daily quota is used up. The audited figures are for the main model.</p>` : "");
      rail.innerHTML = `<h3>Cards pulled · ${data.citations.length}</h3>` +
        (data.citations.length ? data.citations.map((c) => cardHtml(c, turn.id, data.answer)).join("")
          : `<div class="empty-card">This answer cited no card. Treat it with care.</div>`);
      status.textContent = `Answer ready, ${data.citations.length} card${data.citations.length === 1 ? "" : "s"} pulled.`;
    }
  } catch (err) {
    body.innerHTML = `<div class="error-card"><p>${escapeHtml(err.message)}</p>
      <button type="button" class="retry" data-question="${escapeHtml(question)}">Try again</button></div>`;
    rail.innerHTML = "";
    input.value = question; resize();
    status.textContent = err.message;
  } finally {
    clearTimeout(slow);
    busy = false; send.disabled = !input.value.trim();
  }
}

// Pull a card: bring it forward, scroll to it, and move focus into it.
function pull(cardId) {
  const card = document.getElementById(cardId);
  if (!card) return;
  card.closest(".rail").querySelectorAll(".card.pulled").forEach((c) => c.classList.remove("pulled"));
  card.classList.add("pulled");
  card.scrollIntoView({ behavior: "smooth", block: "center" });
  card.focus({ preventScroll: true });
}

document.addEventListener("click", (e) => {
  const mark = e.target.closest(".mark");
  if (mark) return pull(mark.dataset.card);
  const retry = e.target.closest(".retry");
  if (retry) { e.target.closest(".turn").remove(); input.value = ""; return ask(retry.dataset.question); }
  const example = e.target.closest(".ask-example, .ask-chip");
  if (example) ask(example.textContent);
});

$("#new-search").addEventListener("click", () => {
  thread.innerHTML = ""; turnCount = 0;
  $("#welcome").removeAttribute("hidden");
  $("#new-search").hidden = true;
  window.scrollTo({ top: 0, behavior: "smooth" });
  input.focus();
});

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const q = input.value;
  input.value = ""; resize(); ask(q);
});
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); }
});
function resize() {
  input.style.height = "auto";
  if (input.value) input.style.height = `${Math.min(input.scrollHeight, 160)}px`;
  const count = $("#count");
  count.hidden = input.value.length < MAX_CHARS - 100;
  count.textContent = `${input.value.length}/${MAX_CHARS}`;
  send.disabled = busy || !input.value.trim();
}
input.addEventListener("input", resize);
const narrow = window.matchMedia("(max-width: 620px)");
const setPlaceholder = () => { input.placeholder = narrow.matches ? "Ask a policy question" : "Ask about time off, benefits, expenses, travel or equity"; };
narrow.addEventListener("change", setPlaceholder);
setPlaceholder();

$("#drawers").innerHTML = DRAWERS.map((d) => `<div class="drawer-group${d.notHeld ? " not-held" : ""}">
  <h2>${escapeHtml(d.name)}</h2>${d.questions.map((q) => `<button type="button" class="ask-example">${escapeHtml(q)}</button>`).join("")}</div>`).join("");
resize();

fetch("/api/results").then((r) => r.json()).then(({ headline: h }) => {
  if (!h || !h.answerable) return;
  const audit = $("#audit");
  audit.innerHTML = `Audited · <b>${Math.round(100 * h.correct / h.answerable)}% correct</b>` +
    (h.unanswerable ? ` · <b>${h.declined}/${h.unanswerable}</b> refusals right` : "");
  audit.setAttribute("aria-label", `Audited on ${h.answerable + h.unanswerable} test questions: ${Math.round(100 * h.correct / h.answerable)}% of answerable questions fully correct, ${h.declined} of ${h.unanswerable} out-of-scope questions correctly refused. Open the report.`);
  audit.hidden = false;
}).catch(() => {});
