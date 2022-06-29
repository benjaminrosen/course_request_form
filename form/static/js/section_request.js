function getIntegerFromString(string) {
  return parseInt(string.match(/\d+/)[0]);
}

export function getEnrollmentCount() {
  let elements = [...document.querySelectorAll("[id^='enrollment_user_']")];
  elements = elements.map((element) => getIntegerFromString(element.id));
  return Math.max(...elements);
}

export function getNext(array) {
  return array.values().next().value;
}

function setExcludeAnnouncementsDisplay(displayValue) {
  const excludeAnnouncements = document.getElementById(
    "id_exclude_announcements"
  );
  excludeAnnouncements.style.display = displayValue;
}

const proxyRequester = document.getElementById("id_proxy_requester");
if (proxyRequester) {
  proxyRequester.addEventListener("change", (event) =>
    setExcludeAnnouncementsDisplay("none")
  );
}

const copyFromCourse = document.getElementById("id_copy_from_course");
if (copyFromCourse) {
  copyFromCourse.addEventListener("change", (event) =>
    setExcludeAnnouncementsDisplay("block")
  );
}

const addAnotherEnrollment = document.getElementById("add_another_enrollment");
addAnotherEnrollment.addEventListener("click", (event) => {
  const enrollmentCount = getEnrollmentCount();
  const hxVals = JSON.stringify({ enrollmentCount });
  event.target.setAttribute("hx-vals", hxVals);
});
