import { getRowValues } from "./user_row.js";

export function handleLoadOrEditButton(button) {
  if (!button) {
    return;
  }
  button.addEventListener("click", (event) => getRowValues(event.target));
}
