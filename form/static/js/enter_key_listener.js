export function addEnterKeyListener() {
  document.addEventListener("keypress", (event) => {
    if (event.key == "Enter") {
      event.preventDefault();
      event.stopImmediatePropagation();
    }
  });
}
