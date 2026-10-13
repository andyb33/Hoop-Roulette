const state = { game: null, keeps: new Set(), busy: false, selectedCategory: null };

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

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
  const badge = code ? `<i class="category-code" aria-hidden="true">${code}</i>` : "";
  const status = category.used ? `<span class="category-status" aria-label="Scored">✓</span>` : "";
  const classes = [category.used && "used", qualifies && "qualified", elite && "elite", selected && "selected", scoredHighlight && "scored-highlight"].filter(Boolean).join(" ");
  return `<button class="category ${classes}" data-category="${category.id}" ${category.used || category.preview === null ? "disabled" : ""}>
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
  $("#bonus-score").textContent = game.bonus ? `+${game.bonus}` : "0";
  $("#bonus-progress").style.width = `${Math.min(100, (game.upper_total / game.upper_target) * 100)}%`;

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
      ? `${player.unavailable_awards.join(" · ")}: actual awards not introduced. First/Second-Team selections still count toward lower categories. N/A stats can be sacrificed for 0.` : "";
  }

  const grouped = game.categories.reduce((groups, item) => {
    (groups[item.section] ||= []).push(item);
    return groups;
  }, {});
  $("#scorecard").innerHTML = ["Stats", "Accolades", "Joker"].map(section => `
    <section class="score-section"><h3>${section}</h3>${(grouped[section] || []).map(categoryRow).join("")}</section>
  `).join("");
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
  $("#score-confirm").classList.toggle("hidden", !player);
  $("#selected-category").textContent = selectedCategory
    ? `${selectedCategory.label} · ${selectedCategory.preview} points`
    : "Choose a scorecard category";
  $("#confirm-score").disabled = !selectedCategory || state.busy;
  $("#confirm-score").textContent = selectedCategory ? (selectedCategory.unavailable ? "Sacrifice for 0" : `Score ${selectedCategory.preview} points`) : "Confirm score";

  if (game.complete) {
    $("#final-score").textContent = game.total_score;
    $("#finished").showModal();
  }
}

function cycleReel(name, finalValue, duration, choices = []) {
  const value = $(`#${name}-value`);
  const slot = value.closest(".slot");
  if (state.keeps.has(name) || reducedMotion.matches) {
    value.textContent = finalValue;
    return Promise.resolve();
  }
  if (!choices.length) choices = [finalValue];
  slot.classList.add("spinning");
  let index = Math.floor(Math.random() * choices.length);
  const timer = window.setInterval(() => {
    value.textContent = choices[index % choices.length];
    index += 1;
  }, 62);
  return new Promise(resolve => {
    window.setTimeout(() => {
      window.clearInterval(timer);
      value.textContent = finalValue;
      slot.classList.remove("spinning");
      slot.classList.add("landed");
      window.setTimeout(() => slot.classList.remove("landed"), 360);
      resolve();
    }, duration);
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
  const seasonDuration = Math.max(jackpot ? 1100 : 700, ((choices.season?.length || 1) + 1) * 62);
  const teamDuration = Math.max(seasonDuration + 380, (choices.team?.length || 1) * 62);
  const playerDuration = Math.max(teamDuration + 460, (choices.player?.length || 1) * 62);
  await Promise.all([
    cycleReel("season", player.season, seasonDuration, choices.season),
    cycleReel("team", player.team, teamDuration, choices.team),
    cycleReel("player", player.name, playerDuration, choices.player),
  ]);
  $("#player-card").classList.remove("is-waiting");
  if (jackpot) {
    jackpotBanner(player.pool, false);
    if (!reducedMotion.matches) {
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
    await animateReels(game);
    setBusy(false);
    render(game);
  } catch (error) {
    $("#message").textContent = error.message;
    setBusy(false);
    if (state.game) render(state.game);
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

async function newGame() {
  if (state.busy) return;
  setBusy(true);
  try {
    const game = await request("/api/new", {});
    state.keeps.clear();
    state.selectedCategory = null;
    $("#finished").close();
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
}

$$(".slot").forEach(button => button.addEventListener("click", () => {
  if (state.busy) return;
  const keep = button.dataset.keep;
  state.keeps.has(keep) ? state.keeps.delete(keep) : state.keeps.add(keep);
  render(state.game);
}));
$("#spin").addEventListener("click", () => spin());
$$("[data-force]").forEach(button => button.addEventListener("click", () => spin(button.dataset.force)));
$("#confirm-score").addEventListener("click", () => score(state.selectedCategory));
$("#new-game").addEventListener("click", newGame);
$("#play-again").addEventListener("click", newGame);

request("/api/state").then(render).catch(error => { $("#message").textContent = error.message; });
