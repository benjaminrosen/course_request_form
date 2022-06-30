import { getElementByEnrollmentCount } from "./enrollment_count.js";
import {
  getSiblings,
  getNext,
  isButton,
  getEnrollmentUserValues,
} from "./enrollment_user.js";

function handlePennkeyEnter(event) {
  if (event.key == "Enter") {
    const siblings = getSiblings(event.target);
    const button = getNext(siblings.filter((element) => isButton(element)));
    const input = getElementByEnrollmentCount("id_user");
    input.blur();
    button.click();
  }
}

function addListeners() {
  const input = getElementByEnrollmentCount("id_user");
  const loadUserButton = getElementByEnrollmentCount("id_load_user");
  const editUserButton = getElementByEnrollmentCount("id_edit");
  const button = loadUserButton || editUserButton;
  if (input) {
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
  if (button) {
    button.addEventListener("click", (event) =>
      getEnrollmentUserValues(event.target)
    );
  }
}

export function addAdditionalEnrollmentsObserver() {
  const additionalEnrollmentsObserver = new MutationObserver(addListeners);
  const additionalEnrollmentsDiv = document.getElementById(
    "id_additional_enrollments"
  );
  const mutationConfig = { childList: true };
  additionalEnrollmentsObserver.observe(
    additionalEnrollmentsDiv,
    mutationConfig
  );
}
