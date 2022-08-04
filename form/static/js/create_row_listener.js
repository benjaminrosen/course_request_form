import { getRowCount } from "./row_count.js";

export function addCreateRowListener(buttonId) {
  const createButton = document.getElementById(buttonId);
  createButton.addEventListener("click", (event) => {
    const idPrefix = `${buttonId}_`;
    const rowCount = getRowCount(idPrefix);
    const hxVals = JSON.stringify({ rowCount });
    event.target.setAttribute("hx-vals", hxVals);
  });
}
