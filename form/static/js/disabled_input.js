import { getPennkeyFromUser } from "./user_row.js";
import { getElementByRowCount, getExistingRows } from "./row_count.js";
import { getSiblings, getNext, isSelect } from "./user_row.js";
import { handleRemoveEnrollment } from "./remove_button.js";

function isBlank(value) {
  const object = value[0];
  return !Object.keys(object).length;
}

export function getAdditionalEnrollments() {
  return document.getElementById("id_additional_enrollments");
}

function addFirstEnrollment(enrollment) {
  const additionalEnrollments = getAdditionalEnrollments();
  additionalEnrollments.value = JSON.stringify([enrollment]);
}

function addAnotherEnrollment(enrollment, existingEnrollments) {
  const additionalEnrollments = getAdditionalEnrollments();
  additionalEnrollments.value = JSON.stringify(
    existingEnrollments.concat([enrollment])
  );
}

function setAdditionalEnrollmentValue(enrollment) {
  const existingEnrollments = getExistingRows("id_additional_enrollments");
  if (isBlank(existingEnrollments)) {
    addFirstEnrollment(enrollment);
  } else {
    addAnotherEnrollment(enrollment, existingEnrollments);
  }
}

function getRole(input) {
  const siblings = getSiblings(input);
  const selects = siblings.filter((element) => isSelect(element));
  const select = getNext(selects);
  return select.value;
}

export function handleDisabledInput(input) {
  if (!input) {
    return;
  }
  const pennkey = getPennkeyFromUser(input);
  const role = getRole(input);
  const enrollmentUser = { user: pennkey, role: role };
  const removeButton = getElementByRowCount("id_remove");
  removeButton.addEventListener("click", handleRemoveEnrollment);
  setAdditionalEnrollmentValue(enrollmentUser);
}
