const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const report = document.getElementById("report");

function rowsTable(run) {
  const body = run.rows.map((r) => `<tr>
    <td>${esc(r.id)}</td>
    <td><span class="verdict v-${esc(r.verdict)}">${esc(r.verdict)}</span></td>
    <td>${r.answerable ? (r.citation_hit ? "yes" : "no") : "–"}</td>
    <td>${esc(r.question)}</td>
    <td>${esc(r.reason)}</td></tr>`).join("");
  return `<div class="table-wrap"><table class="verdicts">
    <thead><tr><th>ID</th><th>Verdict</th><th>Right page cited</th><th>Question</th><th>Why</th></tr></thead>
    <tbody>${body}</tbody></table></div>`;
}

fetch("/api/results").then((r) => r.json()).then((d) => {
  if (!d.runs?.length) { document.getElementById("intro").textContent = "No evaluation results yet."; return; }
  const h = d.headline, final = d.runs.find((r) => r.mode === "final") || d.runs[d.runs.length - 1];
  const metrics = Object.keys(final.metrics);
  const overrides = d.runs.reduce((n, r) => n + r.overridden, 0);
  report.innerHTML = `
    <h1>How the answers were measured</h1>
    <p>The assistant was tested on <strong>${h.answerable + h.unanswerable} questions written before any tuning</strong>: ${h.answerable} whose answers are in the handbook (6 of them need two sections or pages combined) and ${h.unanswerable} that the handbook does not answer. Every gold answer was copied from the pinned handbook pages, and every out-of-scope question was checked by searching the pages for it.</p>
    <p>Answers come from <code>${esc(d.answer_model)}</code>. A different model family, <code>${esc(d.judge_model)}</code>, judged each answer against the gold answer <strong>and the passages it cited</strong>. Then every verdict was read by hand; ${overrides} were changed across both runs, each with its reason recorded.</p>

    <h2>Results</h2>
    <p>The final setup answers <strong>${h.correct} of ${h.answerable}</strong> answerable questions fully correctly and correctly refuses <strong>${h.declined} of ${h.unanswerable}</strong> out-of-scope questions.</p>
    <p>${d.runs.map((r) => `<strong>${esc(r.name.split(":")[0])}:</strong> ${esc(r.name.split(":").slice(1).join(":").trim())}.`).join(" ")}</p>
    <div class="table-wrap"><table>
      <thead><tr><th>Metric</th>${d.runs.map((r) => `<th class="num">${esc(r.name.split(":")[0])}</th>`).join("")}</tr></thead>
      <tbody>${metrics.map((m) => `<tr><td>${esc(m)}</td>${d.runs.map((r) => `<td class="num">${esc(r.metrics[m]).replace(/ \((.+)\)$/, ' <span class="frac">($1)</span>')}</td>`).join("")}</tr>`).join("")}
      <tr><td>Verdicts changed by human review</td>${d.runs.map((r) => `<td class="num">${r.overridden}</td>`).join("")}</tr></tbody>
    </table></div>

    <h2>Why the final setup</h2>
    <ul>
      <li><strong>It knows when to stop.</strong> Its prompt makes it cite every sentence and refuse with a fixed phrase when the sources don't cover the question.</li>
      <li><strong>Hybrid search finds the right page more often.</strong> Keyword search (BM25) catches exact terms like "401(k)" that meaning-based search alone can miss.</li>
      <li><strong>Known failure:</strong> for "daily meal limit when traveling", hybrid search pulled the Sponsored Travel per-diem rules, and the answer missed the $120/day limit.</li>
      <li>Both setups ran on the same frozen set, which was also used to compare them, so treat the numbers as optimistic for unseen questions.</li>
    </ul>

    <h2>Every verdict</h2>
    ${d.runs.slice().reverse().map((r) => `<details${r.mode === "final" ? " open" : ""}><summary>${esc(r.name)}</summary>${rowsTable(r)}</details>`).join("")}`;
}).catch(() => { document.getElementById("intro").textContent = "Couldn't load the evaluation. Please refresh."; });
