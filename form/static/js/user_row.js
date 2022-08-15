import { getIntegerFromString } from "./row_count.js";

export function getNext(array) {
  return array.values().next().value;
}

function isInput(element) {
  return element.tagName == "INPUT";
}

export function isSelect(element) {
  return element.tagName == "SELECT";
}

export function isButton(element) {
  return element.tagName == "BUTTON";
}

export function getSiblings(element, nested) {
  if (!nested) {
    return [...element.parentElement.children];
  }
  const elements = [...element.parentElement.parentElement.children];
  return elements.map(element => [...element.children]).flat()
}

export function getPennkeyFromUser(input) {
  const regExp = /\(([^)]+)\)/;
  return regExp.exec(input.value)[1];
}

function getPennkeyInput(element) {
  const siblings = getSiblings(element, true);
  const input = siblings.filter((element) => isInput(element));
  return getNext(input).value;
}

export function getRowValues(target) {
  const rowCount = getIntegerFromString(target.id);
  const pennkey = getPennkeyInput(target);
  const values = { rowCount, pennkey };
  const hxVals = JSON.stringify(values);
  target.setAttribute("hx-vals", hxVals);
}
