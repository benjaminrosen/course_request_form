export function getIntegerFromString(string) {
  return parseInt(string.match(/\d+/)[0]);
}

export function getEnrollmentCount() {
  let elements = [...document.querySelectorAll("[id^='id_enrollment_user_']")];
  elements = elements.map((element) => getIntegerFromString(element.id));
  return elements.length ? Math.max(...elements) : 0;
}

export function getElementByEnrollmentCount(elementId) {
  const enrollmentCount = getEnrollmentCount();
  return document.getElementById(`${elementId}_${enrollmentCount}`);
}
