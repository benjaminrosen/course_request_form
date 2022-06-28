function getIntegerFromString(string) {
  return parseInt(string.match(/\d+/)[0]);
}

function getEnrollmentCount() {
  let elements = [...document.querySelectorAll('[id^="enrollment_user"]')];
  elements = elements.map((element) => getIntegerFromString(element.id));
  return Math.max(elements);
}

function isInput(element) {
  const tagName = element.tagName;
  return tagName == "INPUT";
}

function isSelect(element) {
  const tagName = element.tagName;
  return tagName == "SELECT";
}

function getNext(array) {
  return array.values().next().value;
}

function getPennkeyAndRole(element) {
  const siblings = [...element.parentElement.children];
  const input = siblings.filter((element) => isInput(element));
  const select = siblings.filter((element) => isSelect(element));
  const pennkey = getNext(input).value;
  const role = getNext(select).value;
  return { pennkey, role };
}

function loadUser() {
  const enrollmentCount = getEnrollmentCount();
  const { pennkey, role } = getPennkeyAndRole(this);
  let hxVals = { enrollmentCount, pennkey, role };
  hxVals = JSON.stringify(hxVals);
  this.setAttribute("hx-vals", hxVals);
}

const loadUserButton = [...document.getElementsByClassName("load-user-button")];
loadUserButton.forEach((button) => {
  button.addEventListener("click", loadUser);
});

function setExcludeAnnouncementsDisplay(displayValue) {
  const excludeAnnouncements = document.getElementById(
    "id_exclude_announcements"
  );
  excludeAnnouncements.style.display = displayValue;
}

const proxyRequester = document.getElementById("id_proxy_requester");
proxyRequester.addEventListener("change", (event) =>
  setExcludeAnnouncementsDisplay("none")
);

const copyFromCourse = document.getElementById("id_copy_from_course");
copyFromCourse.addEventListener("change", (event) =>
  setExcludeAnnouncementsDisplay("block")
);
