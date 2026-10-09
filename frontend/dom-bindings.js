// Generic DOM helpers used by the pray page's signal bindings.

const FOCUSABLE_SELECTOR = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

// An inline display override, so the stylesheet's display value applies again when shown
export function setShown(element, shown) {
  element.style.display = shown ? '' : 'none';
}

// Page scrolling is locked while any trap is active. Traps can overlap (opening one panel straight from another), so
// the page's own styles are saved by the first lock and restored only when the last is released.
let scrollLocks = 0;
let unlockedStyles = null;

function lockScroll() {
  let root = document.documentElement;
  if (scrollLocks == 0) {
    unlockedStyles = {overflow: root.style.overflow, paddingRight: root.style.paddingRight};
    // Pad by the scrollbar's width so the page doesn't shift sideways when the scrollbar disappears
    root.style.paddingRight = `${window.innerWidth - root.clientWidth}px`;
    root.style.overflow = 'hidden';
  }
  scrollLocks++;
}

function unlockScroll() {
  scrollLocks--;
  if (scrollLocks == 0) {
    document.documentElement.style.overflow = unlockedStyles.overflow;
    document.documentElement.style.paddingRight = unlockedStyles.paddingRight;
  }
}

// Keeps Tab focus inside container and stops the page behind it from scrolling.
// Returns a function that releases the trap and returns focus to where it was.
export function trapFocus(container) {
  let previouslyFocused = document.activeElement;
  lockScroll();

  let focusableElements = () => [...container.querySelectorAll(FOCUSABLE_SELECTOR)].filter(element => element.offsetParent !== null);
  focusableElements()[0]?.focus();

  function onKeydown(event) {
    if (event.key != 'Tab') return;
    let elements = focusableElements();
    if (elements.length == 0) return;
    let first = elements[0];
    let last = elements[elements.length - 1];
    if (event.shiftKey && document.activeElement == first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement == last) {
      event.preventDefault();
      first.focus();
    }
  }
  document.addEventListener('keydown', onKeydown);

  return () => {
    document.removeEventListener('keydown', onKeydown);
    unlockScroll();
    // If another trap has taken focus since (a panel opened straight from this one), leave it there
    if (container.contains(document.activeElement) || document.activeElement == document.body) {
      previouslyFocused?.focus?.();
    }
  };
}

// Calls close on any click outside element while isOpen. Clicks on toggleButton are left to its own handler,
// which would otherwise see the panel closed here and immediately reopen it.
export function closeOnOutsideClick(element, isOpen, close, toggleButton) {
  document.addEventListener('click', (event) => {
    if (!isOpen.value) return;
    if (element.contains(event.target) || toggleButton?.contains(event.target)) return;
    close();
  });
}

// Places a position: fixed element under anchor with their left edges aligned, kept at least margin pixels inside
// the window
export function positionUnderLeftAligned(element, anchor, margin = 8) {
  let anchorRect = anchor.getBoundingClientRect();
  let left = anchorRect.left;
  element.style.left = `${Math.min(Math.max(left, margin), window.innerWidth - element.offsetWidth - margin)}px`;
  element.style.top = `${anchorRect.bottom + 4}px`;
}

export function labelFor(input) {
  return document.querySelector(`label[for="${input.id}"]`);
}
