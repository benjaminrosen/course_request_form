import { getElementByEnrollmentCount } from "./enrollment_count.js";
import { getSiblings, getNext, isButton } from "./enrollment_user.js";

function handlePennkeyEnter(event) {
  if (event.key == "Enter") {
    const siblings = getSiblings(event.target);
    const button = getNext(siblings.filter((element) => isButton(element)));
    const input = getElementByEnrollmentCount("id_user");
    input.blur();
    button.click();
  }
}

export function handleEnabledInput(input) {
  if (!input) {
    return;
  }
  input.addEventListener("focus", (event) => {
    document.addEventListener("keypress", handlePennkeyEnter);
  });
  input.addEventListener("blur", (event) => {
    document.removeEventListener("keypress", handlePennkeyEnter);
  });
  if (input.value) {
    input.focus();
  }
}
