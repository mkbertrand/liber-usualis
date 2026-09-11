<script>
  (function() {
      const stored = localStorage.getItem('theme');
      const theme = stored || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      document.documentElement.setAttribute('data-theme', theme);
  })();
</script>
