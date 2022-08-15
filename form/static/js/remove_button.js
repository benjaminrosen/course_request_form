import { getPennkeyFromUser } from "./user_row.js";
import { getElementByRowCount, getExistingRows } from "./row_count.js"

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
  const additionalEnrollments = document.getElementById("id_additional_enrollments");
  additionalEnrollments.value = JSON.stringify(newEnrollments);
}

export function handleRemoveEnrollment() {
  const disabledInput = getElementByRowCount("id_pennkey");
  const pennkey = getPennkeyFromUser(disabledInput);
  const existingEnrollments = getExistingRows("id_additional_enrollments");
  existingEnrollments.forEach((enrollment) =>
    removeEnrollmentByPennkey(pennkey, enrollment, existingEnrollments)
  );
}
