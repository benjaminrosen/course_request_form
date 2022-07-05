import { getElementByEnrollmentCount } from "./enrollment_count.js";
import { getSiblings, getNext, isButton } from "./enrollment_user.js";
import { handleDisabledInput } from "./disabled_input.js";
import { handleEnabledInput } from "./enabled_input.js";
import { handleLoadOrEditButton } from "./load_or_edit_button.js";
import { handleRemoveEnrollment } from "./remove_button.js";

export function getPennkey(input) {
  const regExp = /\(([^)]+)\)/;
  return regExp.exec(input.value)[1];
}

export function getAdditionalEnrollments() {
  return document.getElementById("id_additional_enrollments");
}

export function getExistingEnrollments() {
  const additionalEnrollments = getAdditionalEnrollments();
  let existingEnrollments = additionalEnrollments.value;
  return JSON.parse(existingEnrollments);
}

export function getDisabledButton() {
  return getElementByEnrollmentCount("id_additional_enrollment_pennkey");
}

function addListeners() {
  const loadUserButton = getElementByEnrollmentCount("id_load_user");
  const editUserButton = getElementByEnrollmentCount("id_edit");
  const loadOrEditbutton = loadUserButton || editUserButton;
  const enabledInput = getElementByEnrollmentCount("id_user");
  const disabledInput = getDisabledButton();
  handleLoadOrEditButton(loadOrEditButton);
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
