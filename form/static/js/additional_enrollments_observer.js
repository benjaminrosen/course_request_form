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

function handleEnabledInput(input) {
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

function handleButton(button) {
  if (!button) {
    return;
  }
  button.addEventListener("click", (event) =>
    getEnrollmentUserValues(event.target)
  );
}

function getPennkey(input) {
  const regExp = /\(([^)]+)\)/;
  return regExp.exec(input.value)[1];
}

function getRole(input) {
  const siblings = getSiblings(input);
  const selects = siblings.filter((element) => isSelect(element));
  const select = getNext(selects);
  return select.value;
}

function isBlank(value) {
  const object = value[0];
  return !Object.keys(object).length;
}

function getExistingEnrollments(element) {
  let existingEnrollments = element.value;
  return JSON.parse(existingEnrollments);
}

function addFirstEnrollment(enrollment, element) {
  element.value = JSON.stringify([enrollment]);
}

function addAnotherEnrollment(enrollment, element) {
  element.value = JSON.stringify(currentValue.concat([enrollment]));
}

function setAdditionalEnrollmentValue(enrollmentUser) {
  const additionalEnrollments = document.getElementById(
    "id_additional_enrollments"
  );
  let existingEnrollments = getExistingEnrollments(additionalEnrollments);
  if (isBlank(existingEnrollments)) {
    addFirstEnrollment(enrollmentUser, additionalEnrollments);
  } else {
    addAnotherEnrollment(enrollmentUser, additionalEnrollments);
  }
}

function handleDisabledInput(input) {
  if (!input) {
    return;
  }
  const pennkey = getPennkey(input);
  const role = getRole(input);
  const enrollmentUser = { user: pennkey, role: role };
  setAdditionalEnrollmentValue(enrollmentUser);
}

function addListeners(list) {
  const loadUserButton = getElementByEnrollmentCount("id_load_user");
  const editUserButton = getElementByEnrollmentCount("id_edit");
  const button = loadUserButton || editUserButton;
  const enabledInput = getElementByEnrollmentCount("id_user");
  const disabledInput = getElementByEnrollmentCount(
    "id_additional_enrollment_pennkey"
  );
  handleButton(button);
  handleEnabledInput(enabledInput);
  handleDisabledInput(disabledInput);
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
