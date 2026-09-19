(() => {
  const input = document.querySelector('[data-grade-file]');
  const status = document.querySelector('[data-grade-status]');
  const output = document.querySelector('[data-grade-output]');
  if (!input || !status || !output) return;
  const format = value => typeof value === 'string' ? value : JSON.stringify(value);
  const passed = value => value === true || (value && value.passed === true);
  const render = result => {
    const checks = result.checks || {};
    output.replaceChildren();
    const table = document.createElement('table');
    const head = document.createElement('thead');
    head.innerHTML = '<tr><th>Check</th><th>Result</th><th>Observed</th><th>Required</th></tr>';
    table.append(head);
    const body = document.createElement('tbody');
    for (const [name, raw] of Object.entries(checks)) {
      const item = typeof raw === 'object' && raw !== null ? raw : {passed: raw};
      const row = document.createElement('tr');
      const values = [name.replaceAll('_', ' '), passed(item) ? 'PASS' : 'FAIL', format(item.observed ?? '—'), format(item.required ?? '—')];
      values.forEach((value, index) => { const cell = document.createElement(index ? 'td' : 'th'); cell.textContent = value; row.append(cell); });
      row.className = passed(item) ? 'grade-check-pass' : 'grade-check-fail';
      body.append(row);
      if (item.message) {
        const detail = document.createElement('tr');
        const cell = document.createElement('td'); cell.colSpan = 4; cell.className = 'grade-check-message'; cell.textContent = item.message;
        detail.append(cell); body.append(detail);
      }
    }
    table.append(body); output.append(table); output.hidden = false;
  };
  input.addEventListener('change', async () => {
    const file = input.files && input.files[0];
    if (!file) return;
    try {
      const result = JSON.parse(await file.text());
      const checks = result.checks || {};
      const failed = Object.entries(checks).filter(([, value]) => !passed(value)).map(([key]) => key);
      render(result);
      if (result.status === 'pass' && failed.length === 0) {
        status.textContent = `Verified ${Object.keys(checks).length} checks from ${file.name}: all passed.`;
        status.className = 'grade-status pass';
        window.CourseAPI?.setComplete(input.dataset.completionKey, true);
      } else {
        status.textContent = `${file.name}: ${failed.length || 1} check(s) failed — ${failed.join(', ') || 'see grader errors'}.`;
        status.className = 'grade-status fail';
        window.CourseAPI?.setComplete(input.dataset.completionKey, false);
      }
    } catch {
      status.textContent = 'That file is not valid grade.json. Export the machine-readable result from the local checker.';
      status.className = 'grade-status fail';
      output.hidden = true;
    }
  });
})();
