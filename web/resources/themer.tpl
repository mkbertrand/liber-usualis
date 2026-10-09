<script>
  (function() {
      // Runs in <head> so the theme is applied before the page is drawn
      let stored = null;
      try {
          stored = localStorage.getItem('theme');
      } catch {
          // Storage unavailable - fall back to the system preference
      }
      const theme = stored || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      document.documentElement.setAttribute('data-theme', theme);

      // The toggle is in the top bar, which isn't parsed yet, so listen on the document
      document.addEventListener('click', (event) => {
          if (!event.target.closest('#dark-mode-toggle')) return;
          const next = document.documentElement.getAttribute('data-theme') == 'dark' ? 'light' : 'dark';
          document.documentElement.setAttribute('data-theme', next);
          try {
              localStorage.setItem('theme', next);
          } catch {
              // Storage unavailable - the theme just isn't remembered
          }
      });
  })();
</script>
