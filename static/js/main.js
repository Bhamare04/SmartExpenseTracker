document.addEventListener('DOMContentLoaded', () => {
  const body = document.body;
  const toggle = document.getElementById('theme-toggle');
  const storageKey = 'smart-expense-tracker-theme';

  const applyTheme = (theme) => {
    body.classList.toggle('dark-mode', theme === 'dark');
    localStorage.setItem(storageKey, theme);
  };

  const storedTheme = localStorage.getItem(storageKey);
  if (storedTheme) {
    applyTheme(storedTheme);
  }

  if (toggle) {
    toggle.addEventListener('click', () => {
      const nextTheme = body.classList.contains('dark-mode') ? 'light' : 'dark';
      applyTheme(nextTheme);
    });
  }

  document.querySelectorAll('[data-autosuggest="true"]').forEach((field) => {
    field.addEventListener('input', (event) => {
      const text = event.target.value.toLowerCase();
      const form = event.target.closest('form');
      const select = form ? form.querySelector('select[name="category"]') : null;
      if (!select) return;

      if (text.match(/coffee|lunch|dinner|meal|restaurant|snack|food/)) select.value = 'Food';
      else if (text.match(/cab|bus|train|metro|fuel|travel|flight/)) select.value = 'Travel';
      else if (text.match(/bill|rent|electricity|water|internet|subscription/)) select.value = 'Bills';
      else if (text.match(/movie|game|netflix|music|concert|party/)) select.value = 'Entertainment';
      else if (text.match(/doctor|medicine|clinic|health|pharmacy/)) select.value = 'Health';
      else if (text.match(/course|book|college|school|tuition|exam/)) select.value = 'Education';
      else if (text.match(/shopping|amazon|mall|purchase|shirt|dress/)) select.value = 'Shopping';
      else select.value = 'Others';
    });
  });

  const chartNode = document.getElementById('chart-data');
  if (chartNode && window.Chart) {
    const payload = JSON.parse(chartNode.textContent);
    const monthly = payload.monthly || { labels: [], income: [], expense: [], savings: [] };
    const categories = payload.categories || { labels: [], values: [] };

    const pieCanvas = document.getElementById('pie-chart');
    const barCanvas = document.getElementById('bar-chart');
    const lineCanvas = document.getElementById('line-chart');
    const savingsCanvas = document.getElementById('savings-chart');

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#dbe6ff' } } },
      scales: {
        x: { ticks: { color: '#a8b4d1' }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { ticks: { color: '#a8b4d1' }, grid: { color: 'rgba(255,255,255,0.04)' } },
      },
    };

    if (pieCanvas) {
      new Chart(pieCanvas, {
        type: 'pie',
        data: {
          labels: categories.labels,
          datasets: [{ data: categories.values, backgroundColor: ['#5cc8ff', '#2b8fff', '#8b7bff', '#2dd4bf', '#ffcc66', '#ff7070', '#9ca3af', '#60a5fa'] }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#dbe6ff' } } } },
      });
    }

    if (barCanvas) {
      new Chart(barCanvas, {
        type: 'bar',
        data: {
          labels: monthly.labels,
          datasets: [{ label: 'Monthly Expenses', data: monthly.expense, backgroundColor: '#5cc8ff' }],
        },
        options: chartOptions,
      });
    }

    if (lineCanvas) {
      new Chart(lineCanvas, {
        type: 'line',
        data: {
          labels: monthly.labels,
          datasets: [
            { label: 'Income', data: monthly.income, borderColor: '#2dd4bf', tension: 0.35, fill: false },
            { label: 'Expense', data: monthly.expense, borderColor: '#ff7070', tension: 0.35, fill: false },
          ],
        },
        options: chartOptions,
      });
    }

    if (savingsCanvas) {
      new Chart(savingsCanvas, {
        type: 'line',
        data: {
          labels: monthly.labels,
          datasets: [{ label: 'Savings Trend', data: monthly.savings, borderColor: '#8b7bff', backgroundColor: 'rgba(139,123,255,0.12)', tension: 0.35, fill: true }],
        },
        options: chartOptions,
      });
    }
  }

  const revealTargets = document.querySelectorAll('.hero-panel, .feature-card, .content-card, .auth-card, .panel, .info-card');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('fade-in');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    revealTargets.forEach((target) => observer.observe(target));
  }
});
