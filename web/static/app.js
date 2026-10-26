const state = { game: null, keeps: new Set(), busy: false, selectedCategory: null, finishedShownId: null, animation: null };

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const desktopMode = new URLSearchParams(window.location.search).get("desktop") === "1";
let desktopSettings = null;
let desktopPending = Promise.resolve();
let desktopPendingCount = 0;
function readSetting(key) {
  if (desktopSettings !== null) return desktopSettings[key] ?? null;
  return localStorage.getItem(key);
}
function saveSetting(key, value) {
  if (desktopMode) {
    if (desktopSettings !== null) desktopSettings[key] = value;
    desktopPendingCount += 1;
    desktopPending = desktopPending.catch(() => {}).then(() => request("/api/desktop-storage", {key, value}))
      .finally(() => { desktopPendingCount -= 1; });
    desktopPending.catch(() => { $("#message").textContent = "Your app settings or scores could not be saved. Please check disk space and permissions."; });
  } else {
    try { localStorage.setItem(key, value); } catch (_) { /* Session state remains available. */ }
  }
}
const INSTANT_STORAGE = "hoopreel.instantSpins.v1";
function readInstantSpins() {
  try { return readSetting(INSTANT_STORAGE) === "true"; }
  catch (_) { return false; }
}
let instantSpins = readInstantSpins();
$("#instant-spins").checked = instantSpins;
function setInstantSpins(enabled) {
  instantSpins = enabled;
  $("#instant-spins").checked = enabled;
  saveSetting(INSTANT_STORAGE, String(enabled));
  if (enabled) skipAnimation();
}

const CATEGORY_CODES = {
  all_nba_third: "NBA 3", all_nba_second: "NBA 2", all_nba_first: "NBA 1",
  champion: "CHAMP", all_defense_second: "DEF 2", all_defense_first: "DEF 1",
  major_award: "MVP+",
};

async function request(path, body = null) {
  const options = body === null ? {} : {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  };
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

function categoryRow(category) {
  const score = category.used ? category.score : category.preview;
  const qualifies = category.section === "Accolades" && !category.used && (category.preview ?? 0) > 0;
  const elite = !category.used && category.glow_threshold && (category.preview ?? 0) >= category.glow_threshold;
  const selected = !category.used && state.selectedCategory === category.id;
  const scoredHighlight = category.used && (
    (category.section === "Accolades" && category.score > 0) ||
    (category.glow_threshold && category.score >= category.glow_threshold)
  );
  const detail = category.used && category.selection
    ? `${category.selection.player} · ${category.selection.season} ${category.selection.team}`
    : category.unavailable ? "N/A this season · sacrifice for 0" : category.preview !== null ? "Available for this player" : "Spin to preview";
  const valueLabel = category.formula || (category.fixed_value ? `${category.fixed_value} pts` : "");
  const code = CATEGORY_CODES[category.id];
  const badge = "";
  const status = category.used ? `<span class="category-status" aria-label="Scored">✓</span>` : "";
  const classes = [category.used && "used", qualifies && "qualified", elite && "elite", selected && "selected", scoredHighlight && "scored-highlight"].filter(Boolean).join(" ");
  return `<button class="category ${classes}" data-category="${category.id}" aria-pressed="${selected}" ${category.used || category.preview === null ? "disabled" : ""}>
    ${badge}<span class="category-copy"><strong>${category.label} <em>${valueLabel}</em></strong><small>${detail}</small></span>
    <b>${!category.used && category.unavailable ? "N/A" : score ?? "—"}</b>${status}
  </button>`;
}

function render(game, { preserveReels = false } = {}) {
  state.game = game;
  if (state.selectedCategory) {
    const selected = game.categories.find(category => category.id === state.selectedCategory);
    if (!selected || selected.used || selected.preview === null) state.selectedCategory = null;
  }

  $("#header-turn").textContent = game.complete ? "Final" : `${game.turn} / ${game.turns_total}`;
  $("#turn-label").textContent = game.complete ? "Game complete" : `Turn ${game.turn} of ${game.turns_total}`;
  $("#spin-label").textContent = game.spins_used ? `Spin ${game.spins_used} of ${game.spins_total}` : "Ready to spin";
  $("#total-score").textContent = game.total_score;
  $("#upper-score").textContent = game.upper_total;
  $("#upper-target").textContent = game.upper_target;
  $("#filled-count").textContent = `${game.categories.filter(c => c.used).length} / ${game.turns_total} filled`;
  $(".bonus-track").setAttribute("aria-valuenow", Math.min(game.upper_total, game.upper_target));
  $(".bonus-track").setAttribute("aria-valuemax", game.upper_target);
  $("#bonus-score").textContent = game.bonus ? `+${game.bonus}` : "0";
  $("#bonus-progress").style.width = `${Math.min(100, (game.upper_total / game.upper_target) * 100)}%`;
  const remaining = Math.max(0, game.upper_target - game.upper_total);
  $("#bonus-remaining").textContent = remaining === 0
    ? "Upper bonus earned!" : `${remaining} point${remaining === 1 ? "" : "s"} to bonus${game.complete ? " · game complete" : ""}`;
  $("#clear-keeps").disabled = state.busy || game.complete || !game.keeps_allowed || game.rerolls_left === 0 || state.keeps.size === 0;

  const player = game.player;
  if (!game.keeps_allowed) state.keeps.clear();
  const jackpot = player && player.pool !== "normal";
  $(".game-panel").dataset.jackpot = jackpot ? player.pool : "";
  $("#jackpot-banner").classList.toggle("hidden", !jackpot);
  if (jackpot) jackpotBanner(player.pool, false);
  $("#dev-jackpots").classList.toggle("hidden", !game.dev_jackpots);
  $$("[data-force]").forEach(button => { button.disabled = state.busy || game.complete || (player && !game.rerolls_left); });
  if (!preserveReels) {
    $("#season-value").textContent = player?.season || "—";
    $("#team-value").textContent = player?.team || "—";
    $("#player-value").textContent = player?.name || "—";
  }

  $("#player-card").classList.toggle("hidden", !player);
  $("#player-empty").classList.toggle("hidden", !!player);
  if (player) {
    $("#player-context").textContent = `${player.season}  ·  ${player.team}`;
    $("#player-name").textContent = player.name;
    $("#jersey").textContent = `#${player.jersey_display}`;
    $("#jersey").style.setProperty("--team-primary", player.team_colors.primary);
    $("#jersey").style.setProperty("--team-secondary", player.team_colors.secondary);
    $("#stats").innerHTML = Object.entries(player.stats)
      .map(([label, value]) => `<div class="${value === null ? "stat-unavailable" : ""}"><strong>${value ?? "N/A"}</strong><span>${label}</span></div>`).join("");
    $("#awards").innerHTML = player.awards.length
      ? player.awards.map(award => `<div class="award-badge"><span>${award.label.split(" ").map(word => word[0]).join("").slice(0, 3)}</span><strong>${award.label}</strong></div>`).join("")
      : `<p class="no-awards">No qualifying accolades</p>`;
    $("#historical-note").classList.toggle("hidden", !player.unavailable_awards.length);
    $("#historical-note").textContent = player.unavailable_awards.length
      ? `${player.unavailable_awards.join(" · ")} not awarded this season. N/A stats may be scored for 0.` : "";
  }

  const grouped = game.categories.reduce((groups, item) => {
    (groups[item.section] ||= []).push(item);
    return groups;
  }, {});
  const classic = [...(grouped.Stats || []), ...(grouped.Joker || [])];
  $("#scorecard").innerHTML = [["Classic stats", classic], ["Accolades", grouped.Accolades || []]].map(([label, categories]) => `
    <section class="score-section" aria-label="${label}"><h3>${label}<span>Points</span></h3>${categories.map(categoryRow).join("")}</section>
  `).join("");
  $$(".category").forEach(button => { button.title = button.textContent.trim().replace(/\s+/g, " "); });
  $$(".category:not(:disabled)").forEach(button => button.addEventListener("click", () => selectCategory(button.dataset.category)));

  $$(".slot").forEach(button => {
    const keepName = button.dataset.keep;
    button.disabled = !player || !game.keeps_allowed || game.rerolls_left === 0 || state.busy;
    button.classList.toggle("kept", state.keeps.has(keepName));
    button.setAttribute("aria-pressed", state.keeps.has(keepName) ? "true" : "false");
    button.querySelector(".keep-text").textContent = jackpot ? "Keeps unavailable" : state.keeps.has(keepName) ? `${keepName} kept` : `Keep ${keepName}`;
  });

  const allKept = state.keeps.size === 3;
  const spinButton = $("#spin");
  spinButton.disabled = state.busy || game.complete || (player && (game.rerolls_left === 0 || allKept));
  spinButton.querySelector(".spin-copy").textContent = player
    ? (game.rerolls_left ? (jackpot ? "Spin again · release jackpot" : "Spin open reels") : "Choose a score")
    : "Spin the roulette";
  $("#spin-count").textContent = player
    ? (game.rerolls_left ? `${game.rerolls_left} reroll${game.rerolls_left === 1 ? "" : "s"} remaining` : "No spins remaining")
    : "3 spins available";

  const selectedCategory = game.categories.find(category => category.id === state.selectedCategory);

  $("#selected-category").textContent = selectedCategory
    ? `${selectedCategory.label} · ${selectedCategory.preview} points`
    : game.complete ? "Game complete · your final scorecard" : player ? "Choose a scorecard category" : "Spin to find your first player";
  $("#confirm-score").disabled = !selectedCategory || state.busy;
  $("#confirm-score").textContent = selectedCategory ? (selectedCategory.unavailable ? "Sacrifice for 0" : `Score ${selectedCategory.preview} points`) : "Confirm score";

  if (game.complete) {
    $("#final-score").textContent = game.total_score;
    $("#final-breakdown").textContent = `Upper: ${game.upper_total} · Bonus: +${game.bonus}`;
    saveCompletedScore(game);
    $("#final-best").textContent = `Personal best: ${scores.best}`;
    if (state.finishedShownId !== game.game_id) {
      state.finishedShownId = game.game_id;
      $("#finished").showModal();
    }
  }
  fitLayout();
}

function skipAnimation() {
  if (!state.animation) return;
  state.animation.skipped = true;
  state.animation.finish?.();
}

function cycleReel(name, finalValue, duration, choices = []) {
  const value = $(`#${name}-value`);
  const slot = value.closest(".slot");
  if (state.keeps.has(name) || reducedMotion.matches || instantSpins || state.animation?.skipped) {
    value.textContent = finalValue;
    return Promise.resolve();
  }
  if (!choices.length) choices = [finalValue];
  slot.classList.add("spinning");
  const timer = window.setInterval(() => {
    value.textContent = choices[Math.floor(Math.random() * choices.length)];
  }, 62);
  return new Promise(resolve => {
    const animation = state.animation;
    let finished = false;
    let timeout;
    const finish = () => {
      if (finished) return;
      finished = true;
      window.clearTimeout(timeout);
      window.clearInterval(timer);
      value.textContent = finalValue;
      slot.classList.remove("spinning");
      if (!animation?.skipped) {
        slot.classList.add("landed");
        window.setTimeout(() => slot.classList.remove("landed"), 360);
      }
      if (animation) animation.finish = null;
      resolve();
    };
    if (animation) animation.finish = finish;
    timeout = window.setTimeout(finish, duration);
  });
}

async function animateReels(game) {
  const player = game.player;
  if (!player) return;
  const jackpot = player.pool !== "normal";
  $("#jackpot-banner").classList.add("hidden");
  $(".game-panel").dataset.jackpot = jackpot ? player.pool : "";
  $(".game-panel").classList.remove("jackpot-hit");
  if (jackpot) {
    state.keeps.clear();
    jackpotBanner(player.pool, true);
    $("#jackpot-banner").classList.remove("hidden");
  }
  $("#player-card").classList.add("is-waiting");
  const choices = game.animation_choices || {};
  // Resolve the context before previewing the next reel; time never grows with pool size.
  const reroll = game.spins_used > 1;
  const durations = jackpot ? [450, 350, 550] : reroll ? [250, 180, 300] : [400, 280, 420];
  for (const name of ["team", "player"]) {
    if (!state.keeps.has(name)) $(`#${name}-value`).textContent = "…";
  }
  await cycleReel("season", player.season, durations[0], choices.season);
  await cycleReel("team", player.team, durations[1], choices.team);
  await cycleReel("player", player.name, durations[2], choices.player);
  $("#player-card").classList.remove("is-waiting");
  if (jackpot) {
    jackpotBanner(player.pool, false);
    if (!reducedMotion.matches && !instantSpins && !state.animation?.skipped) {
      $(".game-panel").classList.add("jackpot-hit");
      $("#jackpot-particles").replaceChildren(...Array.from({ length: 16 }, (_, i) => {
        const particle = document.createElement("i");
        particle.style.setProperty("--x", `${(i / 15) * 100}%`);
        particle.style.setProperty("--delay", `${(i % 4) * 70}ms`);
        return particle;
      }));
      window.setTimeout(() => { $(".game-panel").classList.remove("jackpot-hit"); $("#jackpot-particles").replaceChildren(); }, 1800);
    }
  }
}

function jackpotBanner(pool, anticipating) {
  $("#jackpot-icon").textContent = pool === "award" ? "🏆" : "🦕";
  $("#jackpot-title").textContent = anticipating ? "A legend is incoming…" : pool === "award" ? "Award Jackpot" : "Prehistoric Jackpot";
  $("#jackpot-note").textContent = anticipating ? "Watch the reels land" : "Score this result or spin again · no Keeps";
}

async function spin(forcePool = null) {
  if (state.busy) return;
  setBusy(true);
  state.selectedCategory = null;
  try {
    if (forcePool) state.keeps.clear();
    const game = await request("/api/spin", { keeps: [...state.keeps], ...(forcePool ? { force_pool: forcePool } : {}) });
    $("#message").textContent = "";
    state.animation = { skipped: false, finish: null };
    $("#skip-animation").disabled = reducedMotion.matches || instantSpins;
    await animateReels(game);
    setBusy(false);
    render(game);
  } catch (error) {
    $("#message").textContent = error.message;
    setBusy(false);
    if (state.game) render(state.game);
  } finally {
    state.animation = null;
    $("#skip-animation").disabled = true;
  }
}

function selectCategory(category) {
  if (state.busy) return;
  state.selectedCategory = state.selectedCategory === category ? null : category;
  render(state.game);
}

async function score(category) {
  if (state.busy || !category) return;
  setBusy(true);
  try {
    const game = await request("/api/score", { category });
    state.keeps.clear();
    state.selectedCategory = null;
    setBusy(false);
    render(game);
  } catch (error) {
    $("#message").textContent = error.message;
    setBusy(false);
    render(state.game);
  }
}

function requestNewGame() {
  if (state.busy) return;
  const game = state.game;
  if (game && !game.complete && (game.spins_used > 0 || game.categories.some(category => category.used))) {
    $("#restart-confirm").showModal();
    return;
  }
  return newGame();
}

function clearKeeps() {
  if (state.busy || !state.game || state.game.complete) return;
  state.keeps.clear();
  render(state.game);
}

async function newGame() {
  if (state.busy) return;
  setBusy(true);
  try {
    const game = await request("/api/new", {});
    state.keeps.clear();
    state.selectedCategory = null;
    $("#finished").close();
    $("#restart-confirm").close();
    setBusy(false);
    render(game);
  } catch (error) {
    $("#message").textContent = error.message;
    setBusy(false);
  }
}

function setBusy(value) {
  state.busy = value;
  document.body.classList.toggle("busy", value);
  $("#new-game").disabled = value;
  $("#play-again").disabled = value;
  $("#confirm-restart").disabled = value;
  $("#clear-keeps").disabled = value || !state.game || state.game.complete || !state.game.keeps_allowed || state.game.rerolls_left === 0 || state.keeps.size === 0;
}

$$(".slot").forEach(button => button.addEventListener("click", () => {
  if (state.busy) return;
  const keep = button.dataset.keep;
  state.keeps.has(keep) ? state.keeps.delete(keep) : state.keeps.add(keep);
  render(state.game);
}));
$("#spin").addEventListener("click", () => spin());
$("#skip-animation").addEventListener("click", skipAnimation);
$("#instant-spins").addEventListener("change", event => setInstantSpins(event.target.checked));
$("#clear-keeps").addEventListener("click", clearKeeps);
$$("[data-force]").forEach(button => button.addEventListener("click", () => spin(button.dataset.force)));
$("#confirm-score").addEventListener("click", () => score(state.selectedCategory));
$("#new-game").addEventListener("click", requestNewGame);
$("#play-again").addEventListener("click", requestNewGame);
$("#cancel-restart").addEventListener("click", () => $("#restart-confirm").close());
$("#confirm-restart").addEventListener("click", newGame);


const SCORE_STORAGE = "hoopreel.scores.v1";
function readScores() {
  try {
    const data = JSON.parse(readSetting(SCORE_STORAGE) || "null");
    if (data && Array.isArray(data.recent) && Number.isFinite(data.best)) {
      data.recent = data.recent.filter(item => item && typeof item.id === "string" && Number.isFinite(item.total)).slice(0, 50);
      return data;
    }
  } catch (_) { /* Storage may be unavailable; gameplay still works. */ }
  return { recent: [], best: 0 };
}
let scores = readScores();
function saveCompletedScore(game) {
  if (game.dev_jackpots || scores.recent.some(item => item.id === game.game_id)) return;
  scores.best = Math.max(scores.best, game.total_score);
  scores.recent.unshift({ id: game.game_id, date: new Date().toISOString(), total: game.total_score,
    upper: game.upper_total, bonus: game.bonus,
    categories: game.categories.map(c => ({ label: c.label, score: c.score, selection: c.selection })) });
  scores.recent = scores.recent.slice(0, 50);
  saveSetting(SCORE_STORAGE, JSON.stringify(scores));
  $("#final-best").textContent = `Personal best: ${scores.best}`;
}
let historyIndex = 0;
function renderScoreHistory() {
  $("#history-best").textContent = `Personal best: ${scores.best}`;
  const list = $("#history-scores");
  list.replaceChildren();
  historyIndex = Math.max(0, Math.min(historyIndex, scores.recent.length - 1));
  const item = scores.recent[historyIndex];
  if (item) {
    const summary = document.createElement("div");
    summary.className = "history-summary";
    const total = document.createElement("strong");
    total.textContent = `${item.total} points`;
    const info = document.createElement("p");
    info.textContent = `${new Date(item.date).toLocaleString()} · Upper: ${item.upper} · Bonus: +${item.bonus}`;
    summary.append(total, info);
    list.append(summary);
    const grid = document.createElement("div");
    grid.className = "history-grid";
    for (const category of item.categories || []) {
      const row = document.createElement("div");
      row.className = "history-row";
      const heading = document.createElement("div");
      const label = document.createElement("span");
      label.textContent = category.label;
      const score = document.createElement("strong");
      score.textContent = category.score;
      heading.append(label, score);
      const pick = category.selection;
      const detail = document.createElement("p");
      detail.textContent = pick ? `${pick.player} · ${pick.season} ${pick.team}` : "—";
      detail.title = detail.textContent;
      row.append(heading, detail);
      grid.append(row);
    }
    list.append(grid);
  } else list.textContent = "Finish a game to save your first score.";
  $("#history-position").textContent = item ? `${historyIndex + 1} / ${scores.recent.length} games` : "No games yet";
  $("#history-previous").disabled = historyIndex === 0;
  $("#history-next").disabled = historyIndex >= scores.recent.length - 1;
  if ($("#score-history").open) fitHistoryDialog();
}
function showScoreHistory() {
  historyIndex = 0;
  renderScoreHistory();
  $("#score-history").showModal();
  fitHistoryDialog();
}
function fitHistoryDialog() {
  const dialog = $("#score-history");
  const scale = Math.min(1, ((window.innerWidth || 1280) - 40) / 800,
    ((window.innerHeight || 860) - 40) / (dialog.scrollHeight || 600));
  dialog.style.setProperty("--dialog-scale", scale);
}
$("#history-previous").addEventListener("click", () => { historyIndex -= 1; renderScoreHistory(); });
$("#history-next").addEventListener("click", () => { historyIndex += 1; renderScoreHistory(); });
$("#view-scorecard").addEventListener("click", () => $("#finished").close());
$("#show-history").addEventListener("click", showScoreHistory);
$("#close-history").addEventListener("click", () => $("#score-history").close());

function fitLayout() {
  const shell = $(".app-shell");
  const width = Math.max(1100, Math.min(1600, window.innerWidth || 1280));
  let height = Math.max(800, Math.min(900, window.innerHeight || 860));
  shell.style.width = `${width}px`;
  shell.style.height = `${height}px`;
  for (let pass = 0; pass < 2; pass++) {
    const overflow = Math.max(0, ...$$(".game-panel, .score-panel, .score-section").map(panel => panel.scrollHeight - panel.clientHeight));
    if (overflow < 1) break;
    height += overflow + 4;
    shell.style.height = `${height}px`;
  }
  const scale = Math.min(1, (window.innerWidth || width) / width, (window.innerHeight || height) / height);
  shell.style.transform = `translate(-50%, -50%) scale(${scale})`;
}
window.addEventListener("resize", fitLayout);
window.addEventListener("resize", () => { if ($("#score-history").open) fitHistoryDialog(); });
fitLayout();

async function initializeGame() {
  try {
    if (desktopMode) {
      desktopSettings = await request("/api/desktop-storage");
      instantSpins = readInstantSpins();
      $("#instant-spins").checked = instantSpins;
      scores = readScores();
      $("#history-storage-note").textContent = "Last 50 games · saved on this device";
    }
    render(await request("/api/state"));
  } catch (error) { $("#message").textContent = error.message; }
}
initializeGame();
