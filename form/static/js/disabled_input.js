import {
  getAdditionalEnrollments,
  getExistingEnrollments,
} from "./additional_enrollments_observer.js";
import { getSiblings, getNext, isSelect } from "./enrollment_user.js";

function isBlank(value) {
  const object = value[0];
  return !Object.keys(object).length;
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
  const existingEnrollments = getExistingEnrollments();
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
  const pennkey = getPennkey(input);
  const role = getRole(input);
  const enrollmentUser = { user: pennkey, role: role };
  const removeButton = getElementByEnrollmentCount("id_remove");
  removeButton.addEventListener("click", handleRemoveEnrollment);
  setAdditionalEnrollmentValue(enrollmentUser);
}
