export function getIntegerFromString(string) {
  return parseInt(string.match(/\d+/)[0]);
}

export function getExistingRows(hiddenInputId) {
  const hiddenInput = document.getElementById(hiddenInputId);
  let existingRows = hiddenInput.value;
  return JSON.parse(existingRows);
}

export function getRowCount(idPrefix) {
  let elements = [];
  if (!idPrefix) {
    let prefixes = ["id_user", "id_pennkey"];
    prefixes = prefixes.map(prefix => [...document.querySelectorAll(`[id^='${prefix}']`)]);
    elements = prefixes.flat();
  } else {
    elements = [...document.querySelectorAll(`[id^='${idPrefix}']`)];
  }
  elements = elements.map((element) => getIntegerFromString(element.id));
  return elements.length ? Math.max(...elements) : 0;
}

export function getElementByRowCount(elementId) {
  const rowCount = getRowCount(elementId);
  return document.getElementById(`${elementId}_${rowCount}`);
}
