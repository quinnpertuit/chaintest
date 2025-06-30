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
  logo.style.maxWidth = '180px';
  logo.style.maxHeight = '180px';
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

  // Insert the top bar at the top of the page (before the chat container)
  const mainContainer = document.querySelector('main') || document.body;
  if (mainContainer.firstChild) {
    mainContainer.insertBefore(topBar, mainContainer.firstChild);
  } else {
    mainContainer.appendChild(topBar);
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
