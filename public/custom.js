// public/custom.js
window.addEventListener('DOMContentLoaded', function () {
  // Helper to get the logo path (dark mode by default)
  function getLogoPath() {
    return '/public/logo_dark.png';
  }

  // Create the top bar container
  const topBar = document.createElement('div');
  topBar.id = 'perform-top-bar';
  topBar.style.display = 'flex';
  topBar.style.flexDirection = 'column';
  topBar.style.alignItems = 'center';
  topBar.style.marginBottom = '24px';
  topBar.style.marginTop = '16px';

  // Logo
  const logo = document.createElement('img');
  logo.src = getLogoPath();
  logo.alt = 'Perform Assistant Logo';
  logo.style.maxWidth = '260px';
  logo.style.maxHeight = '260px';
  logo.style.marginBottom = '12px';
  logo.id = 'perform-logo-img';
  topBar.appendChild(logo);

  // Button group
  const buttonGroup = document.createElement('div');
  buttonGroup.id = 'perform-mode-buttons';
  buttonGroup.style.display = 'flex';
  buttonGroup.style.gap = '12px';
  buttonGroup.style.marginBottom = '8px';

  const modes = [
    { key: 'goals', label: 'Goals' },
    { key: 'feedback', label: 'Feedback' },
    { key: 'self', label: 'Self-Assessment' }
  ];

  // Get or set default mode
  let selectedMode = localStorage.getItem('perform_mode') || 'goals';
  localStorage.setItem('perform_mode', selectedMode);

  // Description element
  const description = document.createElement('div');
  description.id = 'perform-description';
  description.style.textAlign = 'center';
  description.style.maxWidth = '600px';
  description.style.margin = '0 auto';
  description.style.padding = '8px 0';
  description.style.fontSize = '14px';
  description.style.lineHeight = '1.5';
  description.style.opacity = '0.8';

  function updateDescription() {
    const descriptions = {
      goals: "I'm here to help you write and achieve your work goals. I can help you clarify objectives, break them down into actionable steps, and provide guidance on goal-setting best practices.",
      feedback: "I'm your expert in giving and receiving professional feedback. I can help you phrase constructive feedback, receive feedback gracefully, and foster a positive feedback culture.",
      self: "I'm your self-assessment specialist. I can help you reflect on your strengths, identify areas for growth, and create actionable self-improvement plans."
    };
    description.textContent = descriptions[selectedMode] || descriptions.goals;
  }

  function updateButtonStyles() {
    modes.forEach(({ key }) => {
      const btn = document.getElementById('perform-btn-' + key);
      if (btn) {
        if (key === selectedMode) {
          btn.classList.add('perform-btn-selected');
        } else {
          btn.classList.remove('perform-btn-selected');
        }
      }
    });
    updateDescription();
  }

  modes.forEach(({ key, label }) => {
    const btn = document.createElement('button');
    btn.textContent = label;
    btn.id = 'perform-btn-' + key;
    btn.className = 'perform-mode-btn';
    btn.onclick = function () {
      selectedMode = key;
      localStorage.setItem('perform_mode', selectedMode);
      updateButtonStyles();
    };
    buttonGroup.appendChild(btn);
  });
  topBar.appendChild(buttonGroup);
  topBar.appendChild(description);

  // Insert the top bar above the main chat container
  const mainContainer = document.querySelector('main');
  if (mainContainer && mainContainer.parentNode) {
    mainContainer.parentNode.insertBefore(topBar, mainContainer);
  } else {
    // fallback: append to body if main not found
    document.body.insertBefore(topBar, document.body.firstChild);
  }

  // Initial button style update
  updateButtonStyles();

  // Update the chat input placeholder
  const interval = setInterval(() => {
    const input = document.querySelector('input[placeholder="Type your message here"]');
    if (input) {
      input.setAttribute(
        'placeholder',
        "Type your message and press Enter..."
      );
      // Intercept Enter key to prepend mode
      input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
          // Prepend the mode as a prefix, e.g. [MODE] message
          const mode = localStorage.getItem('perform_mode') || 'goals';
          if (!input.value.startsWith(`[${mode.toUpperCase()}] `)) {
            input.value = `[${mode.toUpperCase()}] ` + input.value;
          }
        }
      }, { capture: true });
      clearInterval(interval);
    }
  }, 100);
});
