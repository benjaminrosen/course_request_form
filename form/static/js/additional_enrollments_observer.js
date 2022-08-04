import { getElementByRowCount } from "./row_count.js";
import { getSiblings, getNext, isButton } from "./user_row.js";
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
  return getElementByRowCount("id_additional_enrollment_pennkey");
}

function addListeners() {
  const loadUserButton = getElementByRowCount("id_load_user");
  const editUserButton = getElementByRowCount("id_edit");
  const loadOrEditButton = loadUserButton || editUserButton;
  const enabledInput = getElementByRowCount("id_user");
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
