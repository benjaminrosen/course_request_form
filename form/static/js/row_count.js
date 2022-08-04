export function getIntegerFromString(string) {
  return parseInt(string.match(/\d+/)[0]);
}

export function getRowCount(idPrefix) {
  let elements = [...document.querySelectorAll(`[id^='${idPrefix}']`)];
  elements = elements.map((element) => getIntegerFromString(element.id));
  return elements.length ? Math.max(...elements) : 0;
}

export function getElementByRowCount(elementId) {
  const rowCount = getRowCount();
  return document.getElementById(`${elementId}_${rowCount}`);
}
