// Executed inside the packaged native window, not a mock DOM.
window.checkDesktopLayout = () => {
  fitLayout();
  const errors = [];
  const selectors = ['.brand-lockup', '.score-header', '.header-actions', '.app-shell', '.category', '.slot', '#spin', '#confirm-score', '#instant-spins', '#skip-animation', '#clear-keeps', '#show-preview'];
  for (const selector of selectors) for (const element of document.querySelectorAll(selector)) {
    const r = element.getBoundingClientRect();
    if (r.left < -1 || r.top < -1 || r.right > innerWidth + 1 || r.bottom > innerHeight + 1)
      errors.push(`${selector} outside viewport: ${JSON.stringify(r.toJSON())}`);
  }
  for (const panel of document.querySelectorAll('.game-panel, .score-panel, .player-card')) {
    if (!panel.classList.contains('hidden') && panel.scrollHeight > panel.clientHeight + 2)
      errors.push(`${panel.className} has vertical overflow ${panel.scrollHeight}/${panel.clientHeight}`);
  }
  const brand = document.querySelector('.brand-lockup').getBoundingClientRect();
  const totals = document.querySelector('.score-header').getBoundingClientRect();
  if (brand.right > totals.left) errors.push('Brand overlaps header scores');
  const columns = [...document.querySelectorAll('.score-section')];
  if (columns.length !== 2 || columns.some(column => column.querySelectorAll('.category').length !== 7))
    errors.push('Expected two columns with seven categories each');
  const a = columns[0].getBoundingClientRect(), b = columns[1].getBoundingClientRect();
  if (Math.abs(a.top - b.top) > 1 || a.right > b.left) errors.push('Scorecard columns are not side by side');
  const confirmation = document.getElementById('score-confirm').getBoundingClientRect();
  for (const category of document.querySelectorAll('.category')) {
    if (category.getBoundingClientRect().bottom > confirmation.top) errors.push('Category overlaps scoring controls');
  }
  const player = document.getElementById('player-card');
  if (!player.classList.contains('hidden') && player.getBoundingClientRect().bottom > document.querySelector('.spin-zone').getBoundingClientRect().top)
    errors.push('Player card overlaps spin controls');
  return {success:errors.length === 0, errors, width:innerWidth, height:innerHeight, categories:document.querySelectorAll('.category').length};
};
window.exerciseDesktopLayout = async () => {
  const reports = [];
  if (state.game.complete) { await newGame(); await spin(); }
  const check = name => {
    const report = window.checkDesktopLayout(); reports.push({name,...report});
    if (!report.success) throw Error(name+': '+report.errors.join('; '));
  };
  check('current');
  state.keeps = new Set(['team','player']); render(state.game);
  if (canPreview()) {
    renderPreview(); document.getElementById('reroll-preview').showModal();
    const d = document.getElementById('reroll-preview');
    if (d.scrollHeight > d.clientHeight + 2) throw Error('Reroll preview requires scrolling');
    d.close();
  }
  clearKeeps();
  const original = state.game;
  const sample = original.player;
  if (sample) {
    render({...original, player:{...sample, name:'Shai Gilgeous-Alexander', pool:'award',
      awards:[{label:'Most Valuable Player'},{label:'NBA Champion'},{label:'All-NBA First Team'},{label:'All-Defensive First Team'}],
      unavailable_awards:['Defensive Player of the Year','All-Defensive Team']}});
    check('long-name-awards-historical-note');
    render({...original, player:{...sample,pool:'prehistoric'}});
    check('prehistoric-jackpot');
    render(original);
  }
  while (!state.game.complete) {
    if (!state.game.player) await spin();
    const category = state.game.categories.find(c => !c.used && c.preview !== null);
    if (!category) throw Error('No selectable score category');
    selectCategory(category.id);
    check('selected-'+category.id);
    await score(category.id);
  }
  document.getElementById('finished').close();
  check('completed-scorecard');
  await desktopPending;
  showScoreHistory();
  const dialog = document.getElementById('score-history');
  if (dialog.scrollHeight > dialog.clientHeight + 2) throw Error('Score history requires scrolling');
  const r = dialog.getBoundingClientRect();
  if (r.left < -1 || r.top < -1 || r.right > innerWidth + 1 || r.bottom > innerHeight + 1)
    throw Error('Score history outside viewport');
  if (document.querySelectorAll('.history-row').length !== 14) throw Error('History missing picks');
  dialog.close();
  return reports;
};
