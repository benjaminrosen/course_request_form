import {
  getAdditionalEnrollments,
  getDisabledButton,
  getPennkey,
  getExistingEnrollments,
} from "./additional_enrollments_observer.js";

function isEquivalent(one, two) {
  one = Object.values(one);
  two = Object.values(two);
  const isEquivalent = one.every((value, index) => {
    if (value != two[index]) {
      return false;
    }
    return true;
  });
  return isEquivalent;
}

function pennkeyMatchesEnrollment(pennkey, enrollment) {
  return Object.values(enrollment).includes(pennkey);
}

function removeEnrollmentByPennkey(pennkey, enrollment, enrollments) {
  if (!pennkeyMatchesEnrollment(pennkey, enrollment)) {
    return;
  }
  const index = enrollments.indexOf(enrollment);
  let newEnrollments = enrollments.filter((enrollment) => {
    return !isEquivalent(enrollment, enrollments[index]);
  });
  newEnrollments = newEnrollments.length ? newEnrollments : [{}];
  const additionalEnrollments = getAdditionalEnrollments();
  additionalEnrollments.value = JSON.stringify(newEnrollments);
}

export function handleRemoveEnrollment() {
  const disabledButton = getDisabledButton();
  const pennkey = getPennkey(disabledButton);
  const existingEnrollments = getExistingEnrollments();
  existingEnrollments.forEach((enrollment) =>
    removeEnrollmentByPennkey(pennkey, enrollment, existingEnrollments)
  );
}
