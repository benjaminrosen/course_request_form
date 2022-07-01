import { getElementByEnrollmentCount } from "./enrollment_count.js";
import {
  getSiblings,
  getNext,
  isButton,
  isSelect,
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

function addListeners(list) {
  const enabledInput = getElementByEnrollmentCount("id_user");
  const disabledInput = getElementByEnrollmentCount(
    "id_additional_enrollment_pennkey"
  );
  const loadUserButton = getElementByEnrollmentCount("id_load_user");
  const editUserButton = getElementByEnrollmentCount("id_edit");
  const button = loadUserButton || editUserButton;
  if (disabledInput) {
    const regExp = /\(([^)]+)\)/;
    const pennkey = regExp.exec(disabledInput.value)[1];
    const siblings = getSiblings(disabledInput);
    const selects = siblings.filter((element) => isSelect(element));
    const select = getNext(selects);
    const role = select.value;
    const enrollmentUser = JSON.stringify({ user: pennkey, role: role });
    const additionalEnrollments = document.getElementById(
      "id_additional_enrollments"
    );
    additionalEnrollments.value = additionalEnrollments.value + enrollmentUser;
  }
  if (enabledInput) {
    enabledInput.addEventListener("focus", (event) => {
      document.addEventListener("keypress", handlePennkeyEnter);
    });
    enabledInput.addEventListener("blur", (event) => {
      document.removeEventListener("keypress", handlePennkeyEnter);
    });
    if (enabledInput.value) {
      enabledInput.focus();
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
    "id_additional_enrollments_form"
  );
  const mutationConfig = { childList: true };
  additionalEnrollmentsObserver.observe(
    additionalEnrollmentsDiv,
    mutationConfig
  );
}
