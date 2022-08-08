import { getRowCount } from "./row_count.js";

export function addCreateRowListener(buttonId) {
  const createButton = document.getElementById(buttonId);
  createButton.addEventListener("click", (event) => {
    const rowCount = getRowCount();
    const hxVals = JSON.stringify({ rowCount });
    event.target.setAttribute("hx-vals", hxVals);
  });
}
