import { getIntegerFromString } from "./enrollment_count.js";

export function getNext(array) {
  return array.values().next().value;
}

function isInput(element) {
  return element.tagName == "INPUT";
}

function isSelect(element) {
  return element.tagName == "SELECT";
}

export function isButton(element) {
  return element.tagName == "BUTTON";
}

export function getSiblings(element) {
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

export function getEnrollmentUserValues(target) {
  const enrollmentCount = getIntegerFromString(target.id);
  const { pennkey, role } = getPennkeyAndRole(target);
  const hxVals = JSON.stringify({ enrollmentCount, pennkey, role });
  target.setAttribute("hx-vals", hxVals);
}
