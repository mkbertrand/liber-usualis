<script defer>
  document.addEventListener('alpine:init', () => {
      Alpine.store('theme', {
          current: document.documentElement.getAttribute('data-theme') || 'light',

          toggle() {
              console.log(this.current);
              this.current = this.current === 'dark' ? 'light' : 'dark';
              console.log(this.current);
              localStorage.setItem('theme', this.current);
          },

          set(value) {
              this.current = value;
              localStorage.setItem('theme', value);
          }
      });
  });
</script>

