import { getElementByRowCount } from "./row_count.js";
import { getSiblings, getNext, isButton } from "./user_row.js";

function handlePennkeyEnter(event) {
  if (event.key == "Enter") {
    const siblings = getSiblings(event.target);
    const button = getNext(siblings.filter((element) => isButton(element)));
    const input = getElementByRowCount("id_user");
    input.blur();
    button.click();
  }
}

export function handleEnabledInput(input) {
  if (!input) {
    return;
  }
  input.addEventListener("focus", () => {
    document.addEventListener("keypress", handlePennkeyEnter);
  });
  input.addEventListener("blur", () => {
    document.removeEventListener("keypress", handlePennkeyEnter);
  });
  if (input.value) {
    input.focus();
  }
}
