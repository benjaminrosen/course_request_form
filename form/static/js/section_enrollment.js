import { getEnrollmentCount, getNext } from "./section_request.js";

function isInput(element) {
  return element.tagName == "INPUT";
}

function isSelect(element) {
  return element.tagName == "SELECT";
}

function getPennkeyAndRole(element) {
  const siblings = [...element.parentElement.children];
  const input = siblings.filter((element) => isInput(element));
  const select = siblings.filter((element) => isSelect(element));
  const pennkey = getNext(input).value;
  const role = getNext(select).value;
  return { pennkey, role };
}

function loadUser(target) {
  const enrollmentCount = getEnrollmentCount();
  const { pennkey, role } = getPennkeyAndRole(target);
  const hxVals = JSON.stringify({ enrollmentCount, pennkey, role });
  target.setAttribute("hx-vals", hxVals);
}

function addButtonListener() {
  const buttons = document.querySelectorAll("[id^='load_user_']");
  buttons.forEach((button) => {
    button.addEventListener("click", (event) => {
      loadUser(event.target);
    });
  });
}

addButtonListener();
