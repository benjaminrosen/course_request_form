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

function getIntegerFromString(string) {
  return parseInt(string.match(/\d+/)[0]);
}

function getEnrollmentCount() {
  let elements = [...document.querySelectorAll("[id^='id_enrollment_user_']")];
  elements = elements.map((element) => getIntegerFromString(element.id));
  return elements.length ? Math.max(...elements) : 0;
}

function getNext(array) {
  return array.values().next().value;
}

function isInput(element) {
  return element.tagName == "INPUT";
}

function isSelect(element) {
  return element.tagName == "SELECT";
}

function isButton(element) {
  return element.tagName == "BUTTON";
}

function getSiblings(element) {
  return [...element.parentElement.children];
}

function getPennkeyAndRole(element) {
  const siblings = getSiblings(element);
  const input = siblings.filter((element) => isInput(element));
  const select = siblings.filter((element) => isSelect(element));
  const pennkey = getNext(input).value;
  const role = getNext(select).value;
  return { pennkey, role };
}

const addAnotherEnrollment = document.getElementById(
  "id_add_another_enrollment"
);
addAnotherEnrollment.addEventListener("click", (event) => {
  const enrollmentCount = getEnrollmentCount();
  const hxVals = JSON.stringify({ enrollmentCount });
  event.target.setAttribute("hx-vals", hxVals);
});

function getEnrollmentUserValues(target) {
  const enrollmentCount = getIntegerFromString(target.id);
  const { pennkey, role } = getPennkeyAndRole(target);
  const hxVals = JSON.stringify({ enrollmentCount, pennkey, role });
  target.setAttribute("hx-vals", hxVals);
}

function getElementByEnrollmentCount(elementId) {
  const enrollmentCount = getEnrollmentCount();
  return document.getElementById(`${elementId}_${enrollmentCount}`);
}

function handlePennkeyEnter(event) {
  if (event.key == "Enter") {
    const siblings = getSiblings(event.target);
    const button = getNext(siblings.filter((element) => isButton(element)));
    const input = getElementByEnrollmentCount("id_user");
    input.blur();
    button.click();
  }
}

const addLoadUserListener = function (mutationList) {
  const input = getElementByEnrollmentCount("id_user");
  const loadUserButton = getElementByEnrollmentCount("id_load_user");
  const editUserButton = getElementByEnrollmentCount("id_edit");
  const button = loadUserButton || editUserButton;
  if (input) {
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
  if (button) {
    button.addEventListener("click", (event) =>
      getEnrollmentUserValues(event.target)
    );
  }
};
const observer = new MutationObserver(addLoadUserListener);
const additionalEnrollmentsDiv = document.getElementById(
  "id_additional_enrollments"
);
const mutationConfig = { childList: true };
observer.observe(additionalEnrollmentsDiv, mutationConfig);

document.addEventListener("keypress", (event) => {
  if (event.key == "Enter") {
    event.preventDefault();
  }
});
